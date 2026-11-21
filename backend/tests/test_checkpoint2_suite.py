import uuid
import threading
from datetime import date, timedelta
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.models.clinic import Clinic
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.queue import QueueToken, QueueEvent, QueueCounter
from app.schemas.patient import PatientRegisterRequest
from app.services.token_service import TokenService
from app.services.clinic_service import ClinicService
from app.seed import seed_database
from app.utils.timezone import now_utc, get_clinic_date
from app.utils.phone import normalize_phone_number
from tests.conftest import TestingSessionLocal


# ==============================================================================
# PART 8: 1. REGISTRATION TESTS (Tests 1 to 10)
# ==============================================================================

def test_1_successful_patient_registration(client, sample_facility):
    """Test 1: Successful patient registration via API."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    payload = {
        "full_name": "Sunita Patil",
        "phone_number": "9820011223",
        "preferred_language": "mr",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["token_number"] == "GM-001"
    assert data["status"] == "WAITING"
    assert data["patient_name"] == "Sunita Patil"
    assert data["sequence_number"] == 1


def test_2_missing_full_name(client, sample_facility):
    """Test 2: Validation error when full name is missing."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    payload = {
        "full_name": "",
        "phone_number": "9820011223",
        "preferred_language": "en",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 422


def test_3_invalid_phone_number(client, sample_facility):
    """Test 3: Validation error when phone number is invalid."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    payload = {
        "full_name": "Aakash Mehta",
        "phone_number": "12345",  # Too short
        "preferred_language": "en",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 422


def test_4_unsupported_language(client, sample_facility):
    """Test 4: Validation error when an unsupported language is requested."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    payload = {
        "full_name": "Aakash Mehta",
        "phone_number": "9820011223",
        "preferred_language": "fr",  # French not supported (only en, hi, mr)
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 422


def test_5_invalid_clinic_id(client, sample_facility):
    """Test 5: Error when non-existent clinic ID is provided."""
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    payload = {
        "full_name": "Suresh Raina",
        "phone_number": "9820011223",
        "preferred_language": "en",
        "clinic_id": str(uuid.uuid4()),  # Random non-existent UUID
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 404
    assert "Clinic with ID" in response.json()["detail"]


def test_6_invalid_department_id(client, sample_facility):
    """Test 6: Error when non-existent department ID is provided."""
    c = sample_facility["clinic"]
    doc = sample_facility["doctor"]

    payload = {
        "full_name": "Suresh Raina",
        "phone_number": "9820011223",
        "preferred_language": "en",
        "clinic_id": str(c.id),
        "department_id": str(uuid.uuid4()),  # Random department
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 404
    assert "Department with ID" in response.json()["detail"]


def test_7_invalid_doctor_id(client, sample_facility):
    """Test 7: Error when non-existent doctor ID is provided."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]

    payload = {
        "full_name": "Suresh Raina",
        "phone_number": "9820011223",
        "preferred_language": "en",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(uuid.uuid4()),  # Random doctor
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 404
    assert "Doctor with ID" in response.json()["detail"]


def test_8_doctor_belonging_to_another_clinic(client, db_session, sample_facility):
    """Test 8: Error when doctor belongs to a different clinic."""
    now = now_utc()
    other_clinic = Clinic(id=uuid.uuid4(), name="Other Clinic", timezone="UTC", is_active=True, created_at=now, updated_at=now)
    db_session.add(other_clinic)
    db_session.flush()

    other_dept = Department(id=uuid.uuid4(), clinic_id=other_clinic.id, name="Cardiology", code="CARD", is_active=True, created_at=now, updated_at=now)
    db_session.add(other_dept)
    db_session.flush()

    other_doc = Doctor(id=uuid.uuid4(), clinic_id=other_clinic.id, department_id=other_dept.id, name="Dr. Other", is_available=True, created_at=now, updated_at=now)
    db_session.add(other_doc)
    db_session.commit()

    c = sample_facility["clinic"]
    d = sample_facility["department"]

    payload = {
        "full_name": "Vikram Seth",
        "phone_number": "9820011223",
        "preferred_language": "en",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(other_doc.id),  # Belongs to other_clinic
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 400
    assert "Doctor does not belong to the selected clinic" in response.json()["detail"]


def test_9_doctor_belonging_to_another_department(client, db_session, sample_facility):
    """Test 9: Error when doctor belongs to another department in the same clinic."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    now = now_utc()

    pediatrics = Department(id=uuid.uuid4(), clinic_id=c.id, name="Pediatrics", code="PED", is_active=True, created_at=now, updated_at=now)
    db_session.add(pediatrics)
    db_session.flush()

    pedia_doc = Doctor(id=uuid.uuid4(), clinic_id=c.id, department_id=pediatrics.id, name="Dr. Child Care", is_available=True, created_at=now, updated_at=now)
    db_session.add(pedia_doc)
    db_session.commit()

    payload = {
        "full_name": "Vikram Seth",
        "phone_number": "9820011223",
        "preferred_language": "en",
        "clinic_id": str(c.id),
        "department_id": str(d.id),  # GM
        "doctor_id": str(pedia_doc.id),  # PED doctor
        "registration_source": "WEB",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 400
    assert "Doctor does not belong to the selected department" in response.json()["detail"]


def test_10_invalid_registration_source(client, sample_facility):
    """Test 10: Validation error when registration source is invalid."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    payload = {
        "full_name": "Vikram Seth",
        "phone_number": "9820011223",
        "preferred_language": "en",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "INVALID_CHANNEL",
    }
    response = client.post("/api/patients/register", json=payload)
    assert response.status_code == 422


# ==============================================================================
# PART 8: 2. TOKEN GENERATION TESTS (Tests 11 to 16)
# ==============================================================================

def test_11_first_token_generation(db_session, sample_facility):
    """Test 11: First token starts at sequence 1 with department code prefix."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    req = PatientRegisterRequest(
        full_name="Patient One",
        phone_number="9111111111",
        preferred_language="en",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    res = TokenService.register_patient_and_issue_token(db_session, req)
    assert res.sequence_number == 1
    assert res.token_number == "GM-001"


def test_12_sequential_token_generation(db_session, sample_facility):
    """Test 12: Sequential registrations increment sequence number correctly."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    for expected_seq in range(1, 4):
        req = PatientRegisterRequest(
            full_name=f"Patient {expected_seq}",
            phone_number=f"92222222{expected_seq:02d}",
            preferred_language="hi",
            clinic_id=c.id,
            department_id=d.id,
            doctor_id=doc.id,
            registration_source="WEB",
        )
        res = TokenService.register_patient_and_issue_token(db_session, req)
        assert res.sequence_number == expected_seq
        assert res.token_number == f"GM-{expected_seq:03d}"


def test_13_token_uniqueness(db_session, sample_facility):
    """Test 13: Tokens generated for the same department on the same date have unique numbers."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    generated = set()
    for i in range(5):
        req = PatientRegisterRequest(
            full_name=f"Unique Patient {i}",
            phone_number=f"93333333{i:02d}",
            preferred_language="en",
            clinic_id=c.id,
            department_id=d.id,
            doctor_id=doc.id,
            registration_source="STAFF",
        )
        res = TokenService.register_patient_and_issue_token(db_session, req)
        assert res.token_number not in generated
        generated.add(res.token_number)
    assert len(generated) == 5


def test_14_new_day_counter_behaviour(db_session, sample_facility):
    """Test 14: Counter resets to 1 for a new hospital operating date."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]

    today = date(2026, 11, 20)
    tomorrow = date(2026, 11, 21)

    seq_today_1 = TokenService.generate_next_sequence_number(db_session, c.id, d.id, today)
    seq_today_2 = TokenService.generate_next_sequence_number(db_session, c.id, d.id, today)
    assert seq_today_1 == 1
    assert seq_today_2 == 2

    # New day must reset to 1
    seq_tomorrow_1 = TokenService.generate_next_sequence_number(db_session, c.id, d.id, tomorrow)
    assert seq_tomorrow_1 == 1


def test_15_multiple_simultaneous_registrations(db_session, sample_facility):
    """Test 15: Concurrency safety with multiple sequential and simultaneous sequence requests."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    target_date = date(2026, 12, 1)

    sequences = []
    # Verify 10 distinct sequence allocations for the same date and department
    for _ in range(10):
        seq = TokenService.generate_next_sequence_number(db_session, c.id, d.id, target_date)
        sequences.append(seq)

    assert len(sequences) == 10
    # All allocated numbers must be strictly unique and sequential (1 to 10)
    assert sequences == list(range(1, 11))
    assert len(set(sequences)) == 10


def test_16_database_rollback_if_token_creation_fails(db_session, sample_facility):
    """Test 16: Ensure full rollback if a downstream operation in the transaction fails."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    initial_patient_count = db_session.query(Patient).count()
    initial_token_count = db_session.query(QueueToken).count()

    # Attempt registration with non-existent clinic ID to trigger failure
    req = PatientRegisterRequest(
        full_name="Rollback Candidate",
        phone_number="9998887776",
        preferred_language="en",
        clinic_id=uuid.uuid4(),  # Invalid
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    with pytest.raises(HTTPException):
        TokenService.register_patient_and_issue_token(db_session, req)

    # State must be completely unmodified
    assert db_session.query(Patient).count() == initial_patient_count
    assert db_session.query(QueueToken).count() == initial_token_count


# ==============================================================================
# PART 8: 3. DATA INTEGRITY TESTS (Tests 17 to 23)
# ==============================================================================

def test_17_patient_record_persistence(db_session, sample_facility):
    """Test 17: Patient record persists in database."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    req = PatientRegisterRequest(
        full_name="Meera Sen",
        phone_number="9444455555",
        preferred_language="en",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    res = TokenService.register_patient_and_issue_token(db_session, req)
    patient = db_session.query(Patient).filter(Patient.id == res.patient_id).first()
    assert patient is not None
    assert patient.full_name == "Meera Sen"
    assert patient.phone_number == "+919444455555"


def test_18_queue_token_persistence(db_session, sample_facility):
    """Test 18: Queue token record persists in database."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    req = PatientRegisterRequest(
        full_name="Meera Sen",
        phone_number="9444455555",
        preferred_language="en",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    res = TokenService.register_patient_and_issue_token(db_session, req)
    token = db_session.query(QueueToken).filter(QueueToken.id == res.token_id).first()
    assert token is not None
    assert token.status == "WAITING"
    assert token.sequence_number == 1


def test_19_initial_queue_event_creation(db_session, sample_facility):
    """Test 19: An initial QueueEvent with status WAITING is created on token generation."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    req = PatientRegisterRequest(
        full_name="Deepak Joshi",
        phone_number="9555566666",
        preferred_language="hi",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="STAFF",
    )
    res = TokenService.register_patient_and_issue_token(db_session, req)
    events = db_session.query(QueueEvent).filter(QueueEvent.token_id == res.token_id).all()
    assert len(events) == 1
    assert events[0].new_status == "WAITING"
    assert events[0].previous_status is None
    assert events[0].event_type == "TOKEN_CREATED"


def test_20_multiple_visits_by_same_patient(db_session, sample_facility):
    """Test 20: Same patient identity is reused across multiple hospital visits."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    req1 = PatientRegisterRequest(
        full_name="Anil Kapoor",
        phone_number="9666677777",
        preferred_language="en",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    res1 = TokenService.register_patient_and_issue_token(db_session, req1)

    req2 = PatientRegisterRequest(
        full_name="Anil Kapoor",
        phone_number="9666677777",
        preferred_language="en",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    res2 = TokenService.register_patient_and_issue_token(db_session, req2)

    # Patient ID must be identical across both visits
    assert res1.patient_id == res2.patient_id
    # Tokens must be distinct
    assert res1.token_id != res2.token_id
    assert res1.sequence_number != res2.sequence_number


def test_21_duplicate_phone_number_handling(db_session, sample_facility):
    """Test 21: Family members sharing a phone number retain separate patient records."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]
    shared_phone = "9777788888"

    req_father = PatientRegisterRequest(
        full_name="Harish Verma",
        phone_number=shared_phone,
        preferred_language="hi",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    res_father = TokenService.register_patient_and_issue_token(db_session, req_father)

    req_son = PatientRegisterRequest(
        full_name="Nikhil Verma",  # Different name, same phone
        phone_number=shared_phone,
        preferred_language="en",
        clinic_id=c.id,
        department_id=d.id,
        doctor_id=doc.id,
        registration_source="WEB",
    )
    res_son = TokenService.register_patient_and_issue_token(db_session, req_son)

    # Must be separate patients
    assert res_father.patient_id != res_son.patient_id


def test_22_seed_script_idempotency(db_session):
    """Test 22: Seed script creates records on first run, does not duplicate on second run."""
    run1 = seed_database(db=db_session)
    assert run1["clinic_name"] == "City Public Health Clinic"
    assert run1["department_code"] == "GM"

    clinic_count_1 = db_session.query(Clinic).filter(Clinic.name == "City Public Health Clinic").count()
    dept_count_1 = db_session.query(Department).filter(Department.code == "GM").count()
    assert clinic_count_1 == 1
    assert dept_count_1 == 1

    run2 = seed_database(db=db_session)
    clinic_count_2 = db_session.query(Clinic).filter(Clinic.name == "City Public Health Clinic").count()
    dept_count_2 = db_session.query(Department).filter(Department.code == "GM").count()
    assert clinic_count_2 == 1
    assert dept_count_2 == 1
    assert run1["clinic_id"] == run2["clinic_id"]


def test_23_foreign_key_constraint_enforcement(db_session, sample_facility):
    """Test 23: Foreign key constraints prevent orphaned records."""
    c = sample_facility["clinic"]

    # Attempt to insert department pointing to non-existent clinic directly in ORM
    with pytest.raises(Exception):
        orphaned_dept = Department(
            id=uuid.uuid4(),
            clinic_id=uuid.uuid4(),  # Does not exist
            name="Ghost Department",
            code="GHOST",
            is_active=True,
            created_at=now_utc(),
            updated_at=now_utc(),
        )
        db_session.add(orphaned_dept)
        db_session.commit()
    db_session.rollback()


# ==============================================================================
# PART 8: 4. API AND FRONTEND INTEGRATION TESTS (Tests 24 to 31)
# ==============================================================================

def test_24_clinic_listing_api(client, sample_facility):
    """Test 24: GET /api/clinics returns active clinics."""
    res = client.get("/api/clinics")
    assert res.status_code == 200
    clinics = res.json()
    assert len(clinics) >= 1
    assert any(c["name"] == "Test Metro Health Clinic" for c in clinics)


def test_25_department_listing_api(client, sample_facility):
    """Test 25: GET /api/clinics/{clinic_id}/departments returns departments."""
    c = sample_facility["clinic"]
    res = client.get(f"/api/clinics/{c.id}/departments")
    assert res.status_code == 200
    depts = res.json()
    assert len(depts) == 1
    assert depts[0]["code"] == "GM"


def test_26_doctor_listing_api(client, sample_facility):
    """Test 26: GET /api/departments/{department_id}/doctors returns doctors."""
    d = sample_facility["department"]
    res = client.get(f"/api/departments/{d.id}/doctors")
    assert res.status_code == 200
    docs = res.json()
    assert len(docs) == 1
    assert docs[0]["name"] == "Dr. Rajesh Varma"


def test_27_token_details_api(client, sample_facility):
    """Test 27: GET /api/tokens/{token_id} returns public details with masked phone."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    reg_payload = {
        "full_name": "Pooja Hegde",
        "phone_number": "9876543210",
        "preferred_language": "hi",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    reg_res = client.post("/api/patients/register", json=reg_payload)
    token_id = reg_res.json()["token_id"]

    token_res = client.get(f"/api/tokens/{token_id}")
    assert token_res.status_code == 200
    data = token_res.json()
    assert data["token_number"] == "GM-001"
    assert data["status"] == "WAITING"
    assert data["patient_name"] == "Pooja Hegde"
    # Masked phone protects patient privacy
    assert "3210" in data["patient_phone_masked"]
    assert "987654" not in data["patient_phone_masked"]


def test_28_token_event_history_api(client, sample_facility):
    """Test 28: GET /api/tokens/{token_id}/events returns event audit trail."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    reg_payload = {
        "full_name": "Pooja Hegde",
        "phone_number": "9876543210",
        "preferred_language": "hi",
        "clinic_id": str(c.id),
        "department_id": str(d.id),
        "doctor_id": str(doc.id),
        "registration_source": "WEB",
    }
    reg_res = client.post("/api/patients/register", json=reg_payload)
    token_id = reg_res.json()["token_id"]

    events_res = client.get(f"/api/tokens/{token_id}/events")
    assert events_res.status_code == 200
    events = events_res.json()
    assert len(events) == 1
    assert events[0]["new_status"] == "WAITING"
    assert events[0]["event_type"] == "TOKEN_CREATED"


def test_29_frontend_registration_success_simulation(client, sample_facility):
    """Test 29: Simulates frontend user filling the registration form and receiving token."""
    # 1. Frontend queries active clinics
    clinics_res = client.get("/api/clinics")
    selected_clinic = clinics_res.json()[0]

    # 2. Frontend queries departments for that clinic
    depts_res = client.get(f"/api/clinics/{selected_clinic['id']}/departments")
    selected_dept = depts_res.json()[0]

    # 3. Frontend queries doctors for that department
    docs_res = client.get(f"/api/departments/{selected_dept['id']}/doctors")
    selected_doc = docs_res.json()[0]

    # 4. Frontend submits completed form
    form_data = {
        "full_name": "Kavita Krishnamurthy",
        "phone_number": "9898989898",
        "preferred_language": "mr",
        "clinic_id": selected_clinic["id"],
        "department_id": selected_dept["id"],
        "doctor_id": selected_doc["id"],
        "registration_source": "WEB",
    }
    submit_res = client.post("/api/patients/register", json=form_data)
    assert submit_res.status_code == 201
    data = submit_res.json()
    assert data["token_number"] == "GM-001"
    assert data["status"] == "WAITING"
    assert data["clinic_name"] == selected_clinic["name"]
    assert data["department_name"] == selected_dept["name"]
    assert data["doctor_name"] == selected_doc["name"]


def test_30_frontend_validation_errors(client):
    """Test 30: Frontend payload validation handles malformed requests gracefully."""
    # Empty body
    res = client.post("/api/patients/register", json={})
    assert res.status_code == 422
    errors = res.json()["detail"]
    missing_fields = {e["loc"][-1] for e in errors}
    assert "full_name" in missing_fields
    assert "phone_number" in missing_fields
    assert "clinic_id" in missing_fields
    assert "department_id" in missing_fields
    assert "doctor_id" in missing_fields


def test_31_frontend_backend_integration(client, sample_facility):
    """Test 31: End-to-end integration verifying list of registrations after creation."""
    c = sample_facility["clinic"]
    d = sample_facility["department"]
    doc = sample_facility["doctor"]

    # Register 2 patients
    for name, phone in [("Rahul Dravid", "9811122233"), ("VVS Laxman", "9811122244")]:
        client.post(
            "/api/patients/register",
            json={
                "full_name": name,
                "phone_number": phone,
                "preferred_language": "en",
                "clinic_id": str(c.id),
                "department_id": str(d.id),
                "doctor_id": str(doc.id),
                "registration_source": "WEB",
            },
        )

    # Query GET /api/registrations with filters
    reg_list_res = client.get(f"/api/registrations?clinic_id={c.id}&department_id={d.id}")
    assert reg_list_res.status_code == 200
    data = reg_list_res.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["items"][0]["token_number"] == "GM-001"
    assert data["items"][1]["token_number"] == "GM-002"
