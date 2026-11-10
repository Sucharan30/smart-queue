"""
Supabase PostgreSQL Independent Connection Test Script
Checkpoint 1: Verifies that Supabase managed PostgreSQL is accessible
using credentials configured in .env (Session Pooler or Direct connection).

Usage:
    python test_db_connection.py
"""

import sys
from app.config import settings
from app.database import get_engine, text

def test_connection():
    print("=" * 65)
    print("  SMART QUEUING - SUPABASE POSTGRESQL INDEPENDENT CONNECTION TEST")
    print("=" * 65)

    db_url = settings.get_database_url()
    if not db_url:
        print("[ERROR] DATABASE_URL is not configured in backend/.env.")
        print("-" * 65)
        print("Please configure backend/.env using backend/.env.example:")
        print("DATABASE_URL=\"postgresql+psycopg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require\"")
        print("=" * 65)
        return False

    # Mask password for display
    masked_url = db_url
    if "@" in db_url and ":" in db_url.split("@")[0]:
        prefix, rest = db_url.split("@", 1)
        protocol_user, _ = prefix.rsplit(":", 1)
        masked_url = f"{protocol_user}:******@{rest}"

    print(f"Target Connection URL : {masked_url}")
    print(f"Current Environment   : {settings.current_env}")
    print("-" * 65)
    print("Attempting to connect to Supabase PostgreSQL...")

    try:
        engine = get_engine()
        if engine is None:
            raise RuntimeError("Engine could not be initialized.")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();")).scalar()
            print("[SUCCESS] Connection established successfully to Supabase!")
            print(f"[INFO] PostgreSQL Server Version:\n       {result}")
            print("-" * 65)
            print("Status: SUPABASE DATABASE OK (Ready for Alembic and Checkpoint 2)")
            print("=" * 65)
            return True
    except Exception as exc:
        print("[ERROR] Failed to connect to Supabase PostgreSQL.")
        print(f"[REASON] {exc}")
        print("-" * 65)
        print("Troubleshooting steps for Supabase:")
        print("1. In Supabase Dashboard -> Project Settings -> Database:")
        print("   - Copy the 'URI' connection string under Connection Pooling (Session mode, port 6543).")
        print("2. Ensure your database password is correctly inserted into the URI.")
        print("3. Ensure '?sslmode=require' is present at the end of the connection string.")
        print("4. Verify your internet connection allows outbound port 6543 / 5432 traffic.")
        print("=" * 65)
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
