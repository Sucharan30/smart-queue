import uuid
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.token import RegistrationListResponse
from app.services.token_service import TokenService

router = APIRouter(prefix="/api/registrations", tags=["Registrations"])


@router.get(
    "",
    response_model=RegistrationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Registrations",
    description="Returns paginated list of patient registrations with optional clinic, department, and date filters.",
)
def list_registrations(
    clinic_id: Optional[uuid.UUID] = Query(None, description="Filter by clinic ID"),
    department_id: Optional[uuid.UUID] = Query(None, description="Filter by department ID"),
    token_date: Optional[date] = Query(None, description="Filter by local operating date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by token status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size limit"),
    db: Session = Depends(get_db),
) -> RegistrationListResponse:
    return TokenService.list_registrations(
        db=db,
        clinic_id=clinic_id,
        department_id=department_id,
        target_date=token_date,
        status_filter=status,
        page=page,
        page_size=page_size,
    )
