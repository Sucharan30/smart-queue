import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.doctor import DoctorResponse
from app.services.clinic_service import ClinicService

router = APIRouter(prefix="/api/departments", tags=["Departments"])


@router.get(
    "/{department_id}/doctors",
    response_model=List[DoctorResponse],
    status_code=status.HTTP_200_OK,
    summary="List Doctors by Department",
)
def list_doctors(
    department_id: uuid.UUID, db: Session = Depends(get_db)
) -> List[DoctorResponse]:
    """Retrieve all available doctors for a specific department."""
    return ClinicService.get_doctors_by_department(db, department_id)
