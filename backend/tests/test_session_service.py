import pytest
from unittest.mock import patch
from app.services.session_service import (
    create_session, get_sessions, get_session, delete_session,
    export_test_cases_csv
)
from app.exceptions import NotFoundError
from app.models.session import SessionStatus


def test_create_session(db, test_user):
    session = create_session(
        db,
        user_id=test_user.id,
        name="My Session",
        requirement="Some requirement",
        context={"product": "App"},
    )
    assert session.id is not None
    assert session.name == "My Session"
    assert session.status == SessionStatus.pending


def test_get_sessions_empty(db, test_user):
    sessions = get_sessions(db, test_user.id)
    assert sessions == []


def test_get_sessions_with_data(db, test_user, test_session):
    sessions = get_sessions(db, test_user.id)
    assert len(sessions) == 1
    assert sessions[0].name == "Test QA Session"


def test_get_session_not_found(db, test_user):
    with pytest.raises(NotFoundError):
        get_session(db, 99999, test_user.id)


def test_delete_session(db, test_user, test_session):
    delete_session(db, test_session.id, test_user.id)
    with pytest.raises(NotFoundError):
        get_session(db, test_session.id, test_user.id)


def test_export_test_cases_csv(db, test_user, test_session, test_output):
    csv_content = export_test_cases_csv(db, test_session.id, test_user.id)
    assert "TC-POS-001" in csv_content
    assert "Successful login" in csv_content
    assert "test_id" in csv_content


def test_export_empty_csv(db, test_user, test_session):
    csv_content = export_test_cases_csv(db, test_session.id, test_user.id)
    assert csv_content == ""
