from datetime import datetime, timezone
from typing import Tuple
from app.config import settings
from app.database import check_database_connection
from app.schemas.health import HealthResponse, ReadinessResponse, DatabaseHealth


class HealthService:
    @staticmethod
    def get_system_health() -> HealthResponse:
        """
        Liveness probe: verifies that the FastAPI process is responsive.
        Includes a non-blocking summary of the database status.
        Never reveals sensitive credentials or database connection strings.
        """
        db_check = check_database_connection()
        db_status = "connected" if db_check["connected"] else "disconnected"

        return HealthResponse(
            application=settings.PROJECT_NAME,
            environment=settings.current_env,
            api="online",
            database=DatabaseHealth(
                status=db_status,
                message=db_check["message"]
            ),
            timestamp=datetime.now(timezone.utc).isoformat()
        )

    @staticmethod
    def get_readiness_status() -> Tuple[bool, ReadinessResponse]:
        """
        Readiness probe: strictly verifies that Supabase PostgreSQL is accessible.
        Returns a tuple of (is_ready: bool, ReadinessResponse).
        """
        db_check = check_database_connection()
        is_ready = bool(db_check["connected"])
        db_status = "connected" if is_ready else "disconnected"

        response_payload = ReadinessResponse(
            status="ready" if is_ready else "not_ready",
            environment=settings.current_env,
            database=DatabaseHealth(
                status=db_status,
                message=db_check["message"]
            ),
            timestamp=datetime.now(timezone.utc).isoformat()
        )
        return is_ready, response_payload
