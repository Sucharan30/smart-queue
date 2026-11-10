from pydantic import BaseModel, Field
from typing import Optional


class DatabaseHealth(BaseModel):
    status: str = Field(..., description="Status of the database connection ('connected' or 'disconnected')")
    message: str = Field(..., description="Sanitized diagnostic message")


class HealthResponse(BaseModel):
    """Liveness probe response model (GET /api/health)"""
    application: str = Field(..., description="Application name")
    environment: str = Field(..., description="Deployment environment")
    api: str = Field(..., description="API operational status ('online')")
    database: DatabaseHealth = Field(..., description="PostgreSQL database connectivity status")
    timestamp: str = Field(..., description="Current ISO-8601 UTC timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "application": "The Cost of Waiting - Smart Queuing for Public Hospitals",
                "environment": "development",
                "api": "online",
                "database": {
                    "status": "connected",
                    "message": "Supabase PostgreSQL connection active and responsive."
                },
                "timestamp": "2026-11-10T16:00:00Z"
            }
        }


class ReadinessResponse(BaseModel):
    """Readiness probe response model (GET /api/ready)"""
    status: str = Field(..., description="System readiness ('ready' or 'not_ready')")
    environment: str = Field(..., description="Deployment environment")
    database: DatabaseHealth = Field(..., description="Database status verification")
    timestamp: str = Field(..., description="Current ISO-8601 UTC timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "ready",
                "environment": "development",
                "database": {
                    "status": "connected",
                    "message": "Supabase PostgreSQL connection active and responsive."
                },
                "timestamp": "2026-11-10T16:00:00Z"
            }
        }
