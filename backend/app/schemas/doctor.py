import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class DoctorBase(BaseModel):
    name: str
    is_available: bool = True


class DoctorResponse(DoctorBase):
    id: uuid.UUID
    clinic_id: uuid.UUID
    department_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
