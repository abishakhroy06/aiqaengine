import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.auth.jwt import create_access_token, hash_password
from app.models.user import User
from app.models.session import QASession, QAOutput, SessionStatus

# Use SQLite in-memory for tests (no PostgreSQL needed)
TEST_DB_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        hashed_password=hash_password("password123"),
        full_name="Test User",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_session(db, test_user):
    session = QASession(
        user_id=test_user.id,
        name="Test QA Session",
        requirement="User should be able to login with email and password",
        context={"product": "Test App", "platform": "Web"},
        template="full",
        status=SessionStatus.complete,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@pytest.fixture
def test_output(db, test_session):
    output = QAOutput(
        session_id=test_session.id,
        scenario_map={
            "main_flows": ["User logs in successfully"],
            "alternate_flows": ["User uses forgot password"],
            "error_flows": ["Invalid credentials entered"],
            "permission_flows": ["Guest access denied"],
            "integration_flows": ["OAuth flow triggered"],
        },
        test_cases={
            "positive": [
                {
                    "test_id": "TC-POS-001",
                    "reference_id": "F-001",
                    "scenario": "Successful login",
                    "requirement_ref": "F-001",
                    "preconditions": "User registered",
                    "steps": "1. Enter email\n2. Enter password\n3. Click login",
                    "test_data": "email: test@example.com, password: password123",
                    "expected_result": "User redirected to dashboard",
                    "priority": "P1",
                    "notes": "",
                }
            ],
            "negative": [],
            "boundary": [],
            "edge": [],
            "permission": [],
        },
        assumptions=["User has a valid email", "Password meets requirements"],
        questions=["What is the session timeout?", "Is 2FA required?"],
        checklist_result={
            "all_items_traced": "Pass",
            "positive_negative_coverage": "Pass",
            "boundary_coverage": "Pass",
            "edge_coverage": "Pass",
            "permission_coverage": "Pass",
            "integration_coverage": "Pass",
            "no_duplicates": "Pass",
            "clear_expected_results": "Pass",
            "no_hallucinated_rules": "Pass",
        },
    )
    db.add(output)
    db.commit()
    db.refresh(output)
    return output
