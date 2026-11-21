"""
Idempotent Database Seed Script
Creates foundation records for Checkpoint 2:
- 1 Sample Clinic ("City Public Health Clinic")
- 1 Sample General Medicine Department ("GM")
- 1 Sample Doctor ("Dr. Ananya Sharma")
Safely re-runnable: Does NOT duplicate records when executed multiple times.
Does NOT create fictional patient records.
"""

import os
import sys
import uuid

# Ensure backend root is on path when run directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, get_engine
from app.models.clinic import Clinic
from app.models.department import Department
from app.models.doctor import Doctor
from app.utils.timezone import now_utc


def seed_database(db: Session | None = None) -> dict:
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        now = now_utc()

        # 1. Seed or retrieve sample Clinic
        clinic_name = "City Public Health Clinic"
        clinic = db.query(Clinic).filter(Clinic.name == clinic_name).first()
        if not clinic:
            clinic = Clinic(
                id=uuid.uuid4(),
                name=clinic_name,
                address="Station Road, Ward 4, Mumbai, Maharashtra 400001",
                timezone="Asia/Kolkata",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(clinic)
            db.flush()
            print(f"[SEED] Created Clinic: '{clinic.name}' ({clinic.id})")
        else:
            print(f"[SEED] Clinic already exists: '{clinic.name}' ({clinic.id})")

        # 2. Seed or retrieve General Medicine Department for this clinic
        dept_code = "GM"
        dept_name = "General Medicine"
        department = (
            db.query(Department)
            .filter(Department.clinic_id == clinic.id, Department.code == dept_code)
            .first()
        )
        if not department:
            department = Department(
                id=uuid.uuid4(),
                clinic_id=clinic.id,
                name=dept_name,
                code=dept_code,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            db.add(department)
            db.flush()
            print(f"[SEED] Created Department: '{department.name}' ({department.code})")
        else:
            print(f"[SEED] Department already exists: '{department.name}' ({department.code})")

        # 3. Seed or retrieve sample Doctor for this department
        doctor_name = "Dr. Ananya Sharma"
        doctor = (
            db.query(Doctor)
            .filter(
                Doctor.clinic_id == clinic.id,
                Doctor.department_id == department.id,
                Doctor.name == doctor_name,
            )
            .first()
        )
        if not doctor:
            doctor = Doctor(
                id=uuid.uuid4(),
                clinic_id=clinic.id,
                department_id=department.id,
                name=doctor_name,
                is_available=True,
                created_at=now,
                updated_at=now,
            )
            db.add(doctor)
            db.flush()
            print(f"[SEED] Created Doctor: '{doctor.name}' ({doctor.id})")
        else:
            print(f"[SEED] Doctor already exists: '{doctor.name}' ({doctor.id})")

        db.commit()
        return {
            "clinic_id": str(clinic.id),
            "clinic_name": clinic.name,
            "department_id": str(department.id),
            "department_code": department.code,
            "department_name": department.name,
            "doctor_id": str(doctor.id),
            "doctor_name": doctor.name,
        }
    except Exception as e:
        db.rollback()
        print(f"[SEED ERROR] Seeding failed: {e}")
        raise
    finally:
        if close_after:
            db.close()


if __name__ == "__main__":
    result = seed_database()
    print("[SUCCESS] Seeding complete:")
    print(result)
