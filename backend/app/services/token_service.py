import uuid
import threading
from datetime import datetime, date
from typing import Tuple, List, Optional
from sqlalchemy import text, func, and_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.clinic import Clinic
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.queue import QueueCounter, QueueToken, QueueEvent
from app.schemas.patient import PatientRegisterRequest
from app.schemas.token import (
    RegistrationResponse,
    TokenDetailResponse,
    TokenEventResponse,
    RegistrationListItem,
    RegistrationListResponse,
)
from app.utils.phone import mask_phone_number
from app.utils.timezone import get_clinic_date, now_utc


_sqlite_counter_lock = threading.Lock()


class TokenService:
    @staticmethod
    def generate_next_sequence_number(
        db: Session, clinic_id: uuid.UUID, department_id: uuid.UUID, token_date: date
    ) -> int:
        """
        Concurrency-safe atomic token sequence generator.
        Uses PostgreSQL ON CONFLICT DO UPDATE with RETURNING to ensure atomic row-level increment
        without race conditions, duplicates, or unsafe COUNT(*) queries.
        Supports fallback for cross-database test runners.
        """
        bind = db.get_bind()
        now = now_utc()
        new_id = uuid.uuid4()

        if bind.dialect.name == "postgresql":
            sql = text("""
                INSERT INTO queue_counters (id, clinic_id, department_id, token_date, last_sequence_number, created_at, updated_at)
                VALUES (:id, :clinic_id, :department_id, :token_date, 1, :now, :now)
                ON CONFLICT (clinic_id, department_id, token_date)
                DO UPDATE SET 
                    last_sequence_number = queue_counters.last_sequence_number + 1,
                    updated_at = :now
                RETURNING last_sequence_number;
            """)
            result = db.execute(
                sql,
                {
                    "id": new_id,
                    "clinic_id": clinic_id,
                    "department_id": department_id,
                    "token_date": token_date,
                    "now": now,
                },
            )
            seq = result.scalar_one()
            return int(seq)
        else:
            # Fallback for SQLite / generic dialect test environments
            with _sqlite_counter_lock:
                counter = (
                    db.query(QueueCounter)
                    .filter(
                        QueueCounter.clinic_id == clinic_id,
                        QueueCounter.department_id == department_id,
                        QueueCounter.token_date == token_date,
                    )
                    .first()
                )
                if not counter:
                    counter = QueueCounter(
                        id=new_id,
                        clinic_id=clinic_id,
                        department_id=department_id,
                        token_date=token_date,
                        last_sequence_number=1,
                        created_at=now,
                        updated_at=now,
                    )
                    db.add(counter)
                    db.flush()
                    return 1
                else:
                    counter.last_sequence_number += 1
                    counter.updated_at = now
                    db.flush()
                    return counter.last_sequence_number

    @staticmethod
    def register_patient_and_issue_token(
        db: Session, request: PatientRegisterRequest
    ) -> RegistrationResponse:
        """
        Registers a walk-in patient and generates an initial queue token within an atomic transaction.
        Enforces:
        - Clinic, department, and doctor relationship integrity.
        - Patient identity separation (distinct from visit/token; preserves multi-person phone sharing).
        - Concurrency-safe daily sequence numbering.
        - Initial QueueEvent creation.
        - Complete rollback on error.
        """
        # 1. Validate Clinic
        clinic = db.query(Clinic).filter(Clinic.id == request.clinic_id).first()
        if not clinic:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clinic with ID '{request.clinic_id}' does not exist.",
            )
        if not clinic.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected clinic is currently inactive.",
            )

        # 2. Validate Department
        department = db.query(Department).filter(Department.id == request.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department with ID '{request.department_id}' does not exist.",
            )
        if not department.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected department is currently inactive.",
            )
        if department.clinic_id != clinic.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department does not belong to the selected clinic.",
            )

        # 3. Validate Doctor
        doctor = db.query(Doctor).filter(Doctor.id == request.doctor_id).first()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Doctor with ID '{request.doctor_id}' does not exist.",
            )
        if doctor.clinic_id != clinic.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor does not belong to the selected clinic.",
            )
        if doctor.department_id != department.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Doctor does not belong to the selected department.",
            )
        if not doctor.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Selected doctor is currently not available.",
            )

        # 4. Patient Identity Policy
        # Match on (normalized phone_number AND case-insensitive full_name)
        # Allows multiple family members to share phone while retaining separate patient identities.
        normalized_name = request.full_name.strip()
        existing_patient = (
            db.query(Patient)
            .filter(
                Patient.phone_number == request.phone_number,
                func.lower(Patient.full_name) == normalized_name.lower(),
            )
            .first()
        )

        now = now_utc()
        if existing_patient:
            patient = existing_patient
            # Update preferred language if changed
            if patient.preferred_language != request.preferred_language:
                patient.preferred_language = request.preferred_language
                patient.updated_at = now
        else:
            patient = Patient(
                id=uuid.uuid4(),
                full_name=normalized_name,
                phone_number=request.phone_number,
                preferred_language=request.preferred_language,
                created_at=now,
                updated_at=now,
            )
            db.add(patient)
            db.flush()  # assign ID without committing outer transaction

        # Derive token date based on clinic's configured timezone
        token_date = get_clinic_date(clinic.timezone)

        # Check for duplicate active registration on the same day for review
        active_existing_token = (
            db.query(QueueToken)
            .filter(
                QueueToken.patient_id == patient.id,
                QueueToken.department_id == department.id,
                QueueToken.token_date == token_date,
                QueueToken.status.in_(["WAITING", "APPROACHING", "CALLED", "READY", "IN_CONSULTATION"]),
            )
            .first()
        )
        has_duplicate_warning = active_existing_token is not None

        # 5. Concurrency-Safe Sequence & Token Number Generation
        seq_num = TokenService.generate_next_sequence_number(
            db=db, clinic_id=clinic.id, department_id=department.id, token_date=token_date
        )
        token_number_str = f"{department.code.upper()}-{seq_num:03d}"

        # 6. Create QueueToken Record
        token_id = uuid.uuid4()
        token = QueueToken(
            id=token_id,
            clinic_id=clinic.id,
            department_id=department.id,
            doctor_id=doctor.id,
            patient_id=patient.id,
            token_date=token_date,
            sequence_number=seq_num,
            token_number=token_number_str,
            registration_source=request.registration_source,
            status="WAITING",
            registration_time=now,
            created_at=now,
            updated_at=now,
        )
        db.add(token)

        # 7. Create Initial QueueEvent
        event = QueueEvent(
            id=uuid.uuid4(),
            token_id=token_id,
            previous_status=None,
            new_status="WAITING",
            event_type="TOKEN_CREATED",
            event_description=f"Token issued via {request.registration_source}. Initial status: WAITING.",
            created_at=now,
            created_by=request.registration_source,
        )
        db.add(event)

        # Commit all atomically
        db.commit()

        return RegistrationResponse(
            token_id=token.id,
            token_number=token.token_number,
            sequence_number=token.sequence_number,
            token_date=token.token_date,
            status=token.status,
            registration_source=token.registration_source,
            registration_time=token.registration_time,
            clinic_id=clinic.id,
            clinic_name=clinic.name,
            department_id=department.id,
            department_name=department.name,
            department_code=department.code,
            doctor_id=doctor.id,
            doctor_name=doctor.name,
            patient_id=patient.id,
            patient_name=patient.full_name,
            patient_phone_masked=mask_phone_number(patient.phone_number),
            preferred_language=patient.preferred_language,
            duplicate_warning=has_duplicate_warning,
            message="Patient registered successfully and queue token issued.",
        )

    @staticmethod
    def get_token_by_id(db: Session, token_id: uuid.UUID) -> TokenDetailResponse:
        """Retrieve sanitized basic token details without exposing raw sensitive patient data."""
        token = db.query(QueueToken).filter(QueueToken.id == token_id).first()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Token with ID '{token_id}' not found.",
            )

        return TokenDetailResponse(
            id=token.id,
            token_number=token.token_number,
            sequence_number=token.sequence_number,
            token_date=token.token_date,
            status=token.status,
            registration_source=token.registration_source,
            registration_time=token.registration_time,
            clinic_name=token.clinic.name,
            department_name=token.department.name,
            department_code=token.department.code,
            doctor_name=token.doctor.name,
            patient_name=token.patient.full_name,
            patient_phone_masked=mask_phone_number(token.patient.phone_number),
            called_at=token.called_at,
            consultation_started_at=token.consultation_started_at,
            completed_at=token.completed_at,
        )

    @staticmethod
    def get_token_events(db: Session, token_id: uuid.UUID) -> List[TokenEventResponse]:
        """Retrieve event history for a specific token."""
        token = db.query(QueueToken).filter(QueueToken.id == token_id).first()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Token with ID '{token_id}' not found.",
            )
        events = (
            db.query(QueueEvent)
            .filter(QueueEvent.token_id == token_id)
            .order_by(QueueEvent.created_at.asc())
            .all()
        )
        return events

    @staticmethod
    def list_registrations(
        db: Session,
        clinic_id: Optional[uuid.UUID] = None,
        department_id: Optional[uuid.UUID] = None,
        target_date: Optional[date] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> RegistrationListResponse:
        """List registrations with pagination and optional clinic/department/date filters."""
        query = db.query(QueueToken)

        if clinic_id:
            query = query.filter(QueueToken.clinic_id == clinic_id)
        if department_id:
            query = query.filter(QueueToken.department_id == department_id)
        if target_date:
            query = query.filter(QueueToken.token_date == target_date)
        if status_filter:
            query = query.filter(QueueToken.status == status_filter)

        total = query.count()
        page = max(page, 1)
        page_size = max(min(page_size, 100), 1)
        total_pages = max(1, (total + page_size - 1) // page_size)

        tokens = (
            query.order_by(QueueToken.token_date.desc(), QueueToken.sequence_number.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        items = [
            RegistrationListItem(
                token_id=t.id,
                token_number=t.token_number,
                sequence_number=t.sequence_number,
                token_date=t.token_date,
                status=t.status,
                registration_source=t.registration_source,
                registration_time=t.registration_time,
                clinic_name=t.clinic.name,
                department_name=t.department.name,
                doctor_name=t.doctor.name,
                patient_name=t.patient.full_name,
                patient_phone_masked=mask_phone_number(t.patient.phone_number),
            )
            for t in tokens
        ]

        return RegistrationListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
