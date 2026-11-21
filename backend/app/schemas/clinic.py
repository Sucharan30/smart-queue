import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ClinicBase(BaseModel):
    name: str
    address: str | None = None
    timezone: str = "Asia/Kolkata"
    is_active: bool = True


class ClinicResponse(ClinicBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
