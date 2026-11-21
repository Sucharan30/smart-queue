import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.clinic import ClinicResponse
from app.schemas.department import DepartmentResponse
from app.services.clinic_service import ClinicService

router = APIRouter(prefix="/api/clinics", tags=["Clinics"])


@router.get(
    "",
    response_model=List[ClinicResponse],
    status_code=status.HTTP_200_OK,
    summary="List Active Clinics",
)
def list_clinics(db: Session = Depends(get_db)) -> List[ClinicResponse]:
    """Retrieve all operational clinics."""
    return ClinicService.get_active_clinics(db)


@router.get(
    "/{clinic_id}/departments",
    response_model=List[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List Departments by Clinic",
)
def list_departments(
    clinic_id: uuid.UUID, db: Session = Depends(get_db)
) -> List[DepartmentResponse]:
    """Retrieve all operational departments for a specific clinic."""
    return ClinicService.get_departments_by_clinic(db, clinic_id)
