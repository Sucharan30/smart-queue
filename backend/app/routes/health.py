from fastapi import APIRouter, status, Response
from fastapi.responses import JSONResponse
from app.schemas.health import HealthResponse, ReadinessResponse
from app.services.health_service import HealthService

router = APIRouter(prefix="/api", tags=["Health & Readiness"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Liveness Probe",
    description="Returns application and API operational status, along with current database connectivity summary. Never exposes credentials."
)
def get_liveness() -> HealthResponse:
    """
    Lightweight liveness probe indicating whether the API process is running.
    """
    return HealthService.get_system_health()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        200: {"description": "Service is ready; database connection verified."},
        503: {"description": "Service not ready; database connection failed or unconfigured."}
    },
    summary="Application Readiness Probe",
    description="Verifies that the Supabase PostgreSQL database is reachable and accepting queries. Returns 503 if unavailable."
)
def get_readiness():
    """
    Readiness probe for cloud orchestrators (Render / Kubernetes) verifying database connectivity.
    """
    is_ready, payload = HealthService.get_readiness_status()
    if is_ready:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=payload.model_dump()
        )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload.model_dump()
    )
