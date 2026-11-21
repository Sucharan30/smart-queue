import uuid
from typing import List
from sqlalchemy.orm import Session
from app.models.clinic import Clinic
from app.models.department import Department
from app.models.doctor import Doctor


class ClinicService:
    @staticmethod
    def get_active_clinics(db: Session) -> List[Clinic]:
        """Fetch all active clinics."""
        return db.query(Clinic).filter(Clinic.is_active == True).order_by(Clinic.name.asc()).all()

    @staticmethod
    def get_departments_by_clinic(db: Session, clinic_id: uuid.UUID) -> List[Department]:
        """Fetch active departments belonging to a specific clinic."""
        return (
            db.query(Department)
            .filter(Department.clinic_id == clinic_id, Department.is_active == True)
            .order_by(Department.name.asc())
            .all()
        )

    @staticmethod
    def get_doctors_by_department(db: Session, department_id: uuid.UUID) -> List[Doctor]:
        """Fetch available doctors belonging to a specific department."""
        return (
            db.query(Doctor)
            .filter(Doctor.department_id == department_id, Doctor.is_available == True)
            .order_by(Doctor.name.asc())
            .all()
        )
