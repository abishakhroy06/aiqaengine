import csv
import io
import logging
from sqlalchemy.orm import Session as DBSession
from app.models.session import QASession, QAOutput, SessionStatus
from app.exceptions import NotFoundError
from app.services.ai_service import generate_qa_output

logger = logging.getLogger(__name__)


def create_session(
    db: DBSession,
    user_id: int,
    name: str,
    requirement: str,
    context: dict,
    template: str = "full",
) -> QASession:
    session = QASession(
        user_id=user_id,
        name=name,
        requirement=requirement,
        context=context,
        template=template,
        status=SessionStatus.pending,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info("Created QA session %d for user %d", session.id, user_id)
    return session


def get_sessions(db: DBSession, user_id: int) -> list[QASession]:
    return (
        db.query(QASession)
        .filter(QASession.user_id == user_id)
        .order_by(QASession.created_at.desc())
        .all()
    )


def get_session(db: DBSession, session_id: int, user_id: int) -> QASession:
    session = db.query(QASession).filter(
        QASession.id == session_id, QASession.user_id == user_id
    ).first()
    if not session:
        raise NotFoundError("QA Session")
    return session


def delete_session(db: DBSession, session_id: int, user_id: int) -> None:
    session = get_session(db, session_id, user_id)
    db.delete(session)
    db.commit()
    logger.info("Deleted QA session %d", session_id)


def run_generation(session_id: int) -> None:
    """
    Background task — creates its own DB session to avoid using a closed
    request-scoped session from the router.
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        session = db.query(QASession).filter(QASession.id == session_id).first()
        if not session:
            logger.error("Session %d not found for generation", session_id)
            return

        session.status = SessionStatus.generating
        db.commit()
        logger.info("Starting AI generation for session %d", session_id)

        result = generate_qa_output(session.requirement, session.context or {})

        output = db.query(QAOutput).filter(QAOutput.session_id == session_id).first()
        if output:
            db.delete(output)
            db.flush()

        output = QAOutput(
            session_id=session_id,
            scenario_map=result.get("scenario_map", {}),
            test_cases=result.get("test_cases", []),
            assumptions=result.get("assumptions", []),
            questions=result.get("questions", []),
            checklist_result=result.get("checklist", result.get("checklist_result", {})),
        )
        db.add(output)
        session.status = SessionStatus.complete
        db.commit()
        logger.info("AI generation complete for session %d", session_id)

    except Exception as e:
        logger.error("AI generation failed for session %d: %s", session_id, e)
        try:
            session = db.query(QASession).filter(QASession.id == session_id).first()
            if session:
                session.status = SessionStatus.failed
                db.commit()
        except Exception:
            pass
    finally:
        db.close()


def export_test_cases_csv(db: DBSession, session_id: int, user_id: int) -> str:
    """
    Export test cases from a session as CSV string.
    """
    session = get_session(db, session_id, user_id)
    output = db.query(QAOutput).filter(QAOutput.session_id == session_id).first()

    if not output or not output.test_cases:
        return ""

    fieldnames = [
        "section", "test_id", "reference_id", "scenario", "requirement_ref", "preconditions",
        "steps", "test_data", "expected_result", "priority", "notes",
    ]

    section_labels = {
        "positive": "I. Positive",
        "negative": "II. Negative",
        "boundary": "III. Boundary",
        "edge": "IV. Edge",
        "permission": "V. Permission",
    }

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    test_cases = output.test_cases
    if isinstance(test_cases, list):
        # Legacy flat format
        for tc in test_cases:
            writer.writerow(tc)
    elif isinstance(test_cases, dict):
        for section_key, label in section_labels.items():
            for tc in test_cases.get(section_key, []):
                writer.writerow({"section": label, **tc})

    return buffer.getvalue()
