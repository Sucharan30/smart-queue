import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.utils.phone import normalize_phone_number, mask_phone_number

SupportedLanguage = Literal["en", "hi", "mr"]
RegistrationSource = Literal["STAFF", "WEB", "WHATSAPP"]


class PatientRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150, description="Full legal name of the patient")
    phone_number: str = Field(..., description="Mobile number for queue notifications")
    preferred_language: SupportedLanguage = Field("en", description="Language preference: 'en', 'hi', or 'mr'")
    clinic_id: uuid.UUID = Field(..., description="ID of the clinic")
    department_id: uuid.UUID = Field(..., description="ID of the department (e.g. General Medicine)")
    doctor_id: uuid.UUID = Field(..., description="ID of the attending doctor")
    registration_source: RegistrationSource = Field("WEB", description="Registration channel ('WEB', 'STAFF', 'WHATSAPP')")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        cleaned = v.strip()
        if len(cleaned) < 2:
            raise ValueError("Full name must be at least 2 characters long.")
        return cleaned

    @field_validator("phone_number")
    @classmethod
    def validate_and_normalize_phone(cls, v: str) -> str:
        return normalize_phone_number(v)


class PatientResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    phone_number_masked: str
    preferred_language: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
