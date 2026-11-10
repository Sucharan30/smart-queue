import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "The Cost of Waiting - Smart Queuing for Public Hospitals"
    API_VERSION: str = "v1"
    APP_ENV: str = "development"
    ENVIRONMENT: Optional[str] = None  # Backward compatibility
    DEBUG: bool = True
    
    # Server Binding (Render automatically provides PORT)
    HOST: str = "0.0.0.0"
    PORT: int = int(os.environ.get("PORT", 8000))

    # CORS & Frontend URLs
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database Configuration (Supabase PostgreSQL via Psycopg 3)
    DATABASE_URL: str = ""
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_SSL_MODE: str = "require"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def current_env(self) -> str:
        """Return canonical environment name."""
        return (self.ENVIRONMENT or self.APP_ENV or "development").lower()

    @property
    def is_production(self) -> bool:
        return self.current_env == "production"

    def get_cors_origins(self) -> List[str]:
        """
        Parses comma-separated CORS origins and adds FRONTEND_URL.
        In production, wildcards are disallowed to ensure strict security.
        """
        origins_set = set()

        if isinstance(self.CORS_ORIGINS, str) and self.CORS_ORIGINS.strip():
            for origin in self.CORS_ORIGINS.split(","):
                cleaned = origin.strip()
                if cleaned:
                    origins_set.add(cleaned)

        if self.FRONTEND_URL and self.FRONTEND_URL.strip():
            origins_set.add(self.FRONTEND_URL.strip())

        # Disallow '*' in production
        if self.is_production and "*" in origins_set:
            origins_set.remove("*")

        return list(origins_set) if origins_set else ["http://localhost:5173", "http://127.0.0.1:5173"]

    def get_database_url(self) -> str:
        """
        Return the SQLAlchemy-compatible database URL with psycopg driver.
        Supports Supabase direct connection or Supabase Session/Transaction Pooler.
        Automatically normalizes 'postgresql://' or 'postgres://' to 'postgresql+psycopg://'.
        """
        url = (self.DATABASE_URL or "").strip()

        if url:
            # Normalize prefix for Psycopg 3 driver
            if url.startswith("postgres://"):
                url = "postgresql+psycopg://" + url[len("postgres://"):]
            elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
                url = "postgresql+psycopg://" + url[len("postgresql://"):]

            # Automatically enforce SSL for cloud-hosted Supabase instances
            if "supabase" in url and "sslmode" not in url:
                separator = "&" if "?" in url else "?"
                url += f"{separator}sslmode=require"

            return url

        # Construct from individual fields if DATABASE_URL is not set directly
        if self.DB_PASSWORD:
            base_url = (
                f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
            if self.DB_SSL_MODE:
                base_url += f"?sslmode={self.DB_SSL_MODE}"
            return base_url

        # Empty placeholder if no credentials are configured yet
        return ""


settings = Settings()
