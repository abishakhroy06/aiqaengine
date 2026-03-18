import io
import logging
from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.session import QASession, QAOutput, SessionStatus
from app.schemas.session import (
    CreateSessionRequest,
    QASessionResponse,
    QASessionListItem,
)
from app.services.file_extractor import extract_text
from app.services.session_service import (
    create_session,
    get_sessions,
    get_session,
    delete_session,
    run_generation,
    export_test_cases_csv,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["sessions"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/extract-text")
async def extract_text_from_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Extract plain text from an uploaded PDF, DOCX, or TXT file."""
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10 MB.")
    try:
        text = extract_text(file.filename or "file.txt", content)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return {"text": text, "filename": file.filename, "char_count": len(text)}


@router.get("", response_model=list[QASessionListItem])
async def list_sessions(
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[QASessionListItem]:
    sessions = get_sessions(db, current_user.id)
    result = []
    for s in sessions:
        output = db.query(QAOutput).filter(QAOutput.session_id == s.id).first()
        if output and output.test_cases:
            tcs = output.test_cases
            if isinstance(tcs, dict):
                tc_count = sum(len(v) for v in tcs.values() if isinstance(v, list))
            else:
                tc_count = len(tcs)
        else:
            tc_count = 0
        item = QASessionListItem(
            id=s.id,
            name=s.name,
            status=s.status,
            created_at=s.created_at,
            updated_at=s.updated_at,
            test_case_count=tc_count,
        )
        result.append(item)
    return result


@router.post("", response_model=QASessionResponse, status_code=201)
async def create_new_session(
    req: CreateSessionRequest,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QASession:
    session = create_session(
        db,
        user_id=current_user.id,
        name=req.name,
        requirement=req.requirement,
        context=req.context.model_dump(),
        template=req.template,
    )
    background_tasks.add_task(run_generation, session.id)
    session.output = None
    return session


@router.get("/{session_id}", response_model=QASessionResponse)
async def get_session_detail(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QASession:
    session = get_session(db, session_id, current_user.id)
    output = db.query(QAOutput).filter(QAOutput.session_id == session_id).first()
    session.output = output
    return session


@router.delete("/{session_id}", status_code=204)
async def delete_session_endpoint(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_session(db, session_id, current_user.id)


@router.post("/{session_id}/regenerate", response_model=QASessionResponse)
async def regenerate_session(
    session_id: int,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QASession:
    session = get_session(db, session_id, current_user.id)
    session.status = SessionStatus.pending
    db.commit()
    db.refresh(session)
    background_tasks.add_task(run_generation, session.id)
    session.output = None
    return session


@router.get("/{session_id}/export")
async def export_session_csv(
    session_id: int,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    csv_content = export_test_cases_csv(db, session_id, current_user.id)
    session = get_session(db, session_id, current_user.id)
    filename = f"test-cases-{session.name.lower().replace(' ', '-')}-{session_id}.csv"
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
