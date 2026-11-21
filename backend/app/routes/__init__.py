from fastapi import APIRouter
from app.routes.health import router as health_router
from app.routes.clinics import router as clinics_router
from app.routes.departments import router as departments_router
from app.routes.patients import router as patients_router
from app.routes.tokens import router as tokens_router
from app.routes.registrations import router as registrations_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(clinics_router)
api_router.include_router(departments_router)
api_router.include_router(patients_router)
api_router.include_router(tokens_router)
api_router.include_router(registrations_router)

__all__ = ["api_router"]
