import os
import sys
import uuid
import pytest

# Ensure backend root is on pythonpath
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models.clinic import Clinic
from app.models.department import Department
from app.models.doctor import Doctor
from app.utils.timezone import now_utc

TEST_DB_FILE = os.path.join(os.path.dirname(__file__), "test_isolated.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Enable foreign keys for SQLite
@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_schema():
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture
def db_session():
    """Provides a transactional database session per test with automatic rollback."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_facility(db_session):
    """Creates a sample clinic, department, and doctor for test isolation."""
    now = now_utc()
    clinic = Clinic(
        id=uuid.uuid4(),
        name="Test Metro Health Clinic",
        address="123 Hospital Road",
        timezone="Asia/Kolkata",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(clinic)
    db_session.flush()

    department = Department(
        id=uuid.uuid4(),
        clinic_id=clinic.id,
        name="General Medicine",
        code="GM",
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(department)
    db_session.flush()

    doctor = Doctor(
        id=uuid.uuid4(),
        clinic_id=clinic.id,
        department_id=department.id,
        name="Dr. Rajesh Varma",
        is_available=True,
        created_at=now,
        updated_at=now,
    )
    db_session.add(doctor)
    db_session.commit()

    return {
        "clinic": clinic,
        "department": department,
        "doctor": doctor,
    }
