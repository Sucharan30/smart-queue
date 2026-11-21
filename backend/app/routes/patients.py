from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.patient import PatientRegisterRequest
from app.schemas.token import RegistrationResponse
from app.services.token_service import TokenService

router = APIRouter(prefix="/api/patients", tags=["Patient Registration"])


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Patient and Issue Queue Token",
    description="Registers walk-in patient, generates next atomic daily token sequence, records initial WAITING queue event, and returns registration details.",
)
def register_patient(
    request: PatientRegisterRequest, db: Session = Depends(get_db)
) -> RegistrationResponse:
    return TokenService.register_patient_and_issue_token(db=db, request=request)
