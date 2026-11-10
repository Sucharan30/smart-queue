import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smart_queue")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    description="Backend API for Smart Queuing System in Public Hospitals (Cloud Architecture: Render + Supabase)",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS with explicitly defined origins
origins = settings.get_cors_origins()
logger.info(f"CORS origins configured: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint confirming service availability and guiding developers to API docs and probes.
    """
    return {
        "project": settings.PROJECT_NAME,
        "environment": settings.current_env,
        "status": "operational",
        "docs": "/docs",
        "liveness_endpoint": "/api/health",
        "readiness_endpoint": "/api/ready"
    }


if __name__ == "__main__":
    import uvicorn
    # Render provides PORT in the environment
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=port,
        reload=settings.DEBUG and not settings.is_production
    )
