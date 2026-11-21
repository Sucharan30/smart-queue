import uuid
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class TokenEventResponse(BaseModel):
    id: uuid.UUID
    token_id: uuid.UUID
    previous_status: str | None = None
    new_status: str
    event_type: str
    event_description: str | None = None
    created_at: datetime
    created_by: str | None = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationResponse(BaseModel):
    token_id: uuid.UUID
    token_number: str
    sequence_number: int
    token_date: date
    status: str
    registration_source: str
    registration_time: datetime

    clinic_id: uuid.UUID
    clinic_name: str

    department_id: uuid.UUID
    department_name: str
    department_code: str

    doctor_id: uuid.UUID
    doctor_name: str

    patient_id: uuid.UUID
    patient_name: str
    patient_phone_masked: str
    preferred_language: str

    duplicate_warning: bool = False
    message: str = "Patient registered successfully and queue token issued."

    model_config = ConfigDict(from_attributes=True)


class TokenDetailResponse(BaseModel):
    id: uuid.UUID
    token_number: str
    sequence_number: int
    token_date: date
    status: str
    registration_source: str
    registration_time: datetime

    clinic_name: str
    department_name: str
    department_code: str
    doctor_name: str

    # Masked for patient privacy
    patient_name: str
    patient_phone_masked: str

    called_at: datetime | None = None
    consultation_started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class RegistrationListItem(BaseModel):
    token_id: uuid.UUID
    token_number: str
    sequence_number: int
    token_date: date
    status: str
    registration_source: str
    registration_time: datetime
    clinic_name: str
    department_name: str
    doctor_name: str
    patient_name: str
    patient_phone_masked: str

    model_config = ConfigDict(from_attributes=True)


class RegistrationListResponse(BaseModel):
    items: list[RegistrationListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
