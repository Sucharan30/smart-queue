# The Cost of Waiting – Smart Queuing for Public Hospitals

A cloud-native, WhatsApp-linked hospital queue management system designed to reduce unnecessary waiting times, protect vulnerable patients from waiting-hall cross-infections, and allow patients to track their queue positions in real time.

---

## Table of Contents
1. [Final System Architecture](#1-final-system-architecture)
2. [Technology Stack](#2-technology-stack)
3. [Project Folder Structure](#3-project-folder-structure)
4. [Prerequisites](#4-prerequisites)
5. [Supabase Database Setup Instructions](#5-supabase-database-setup-instructions)
6. [Configuring `DATABASE_URL` and Enabling SSL](#6-configuring-database_url-and-enabling-ssl)
7. [Local Backend Setup and Execution](#7-local-backend-setup-and-execution)
8. [Alembic Database Migrations](#8-alembic-database-migrations)
9. [Local Frontend Setup and Execution](#9-local-frontend-setup-and-execution)
10. [Deploying Backend to Render](#10-deploying-backend-to-render)
11. [Deploying Frontend to Vercel](#11-deploying-frontend-to-vercel)
12. [Environment Variable Reference for Both Platforms](#12-environment-variable-reference-for-both-platforms)
13. [Verification & Health Probes](#13-verification--health-probes)
14. [How to Upload to GitHub](#14-how-to-upload-to-github)

---

## 1. Final System Architecture

```
┌────────────────────────────────────────────────────────┐
│             Frontend (Hosted on Vercel)                │
│  - React.js 18 + Vite + Tailwind CSS                   │
│  - Single Page Application with client-side routing    │
│  - Axios HTTP client targeting Render backend          │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS REST API requests
┌───────────────────────────▼────────────────────────────┐
│             Backend (Hosted on Render)                 │
│  - Python 3.10+ with FastAPI & Uvicorn ASGI            │
│  - Strict CORS origin whitelisting                     │
│  - Liveness (/api/health) & Readiness (/api/ready)     │
│  - Alembic automated database migration pipeline       │
└───────────────────────────┬────────────────────────────┘
                            │ Encrypted TLS/SSL Connection (Psycopg 3)
                            │ via Session Pooler (Port 6543)
┌───────────────────────────▼────────────────────────────┐
│             Database (Supabase PostgreSQL)             │
│  - Managed PostgreSQL instance with connection pooling │
│  - High-availability, scalable relational storage      │
└────────────────────────────────────────────────────────┘
```

> **Strict Security Boundary:** The React frontend **never** connects directly to PostgreSQL or Supabase. All database access, authentication, and queuing logic are mediated through the FastAPI backend.

---

## 2. Technology Stack

- **Frontend:** React.js, Vite, Tailwind CSS, React Router v6, Axios, Lucide React (Hosted on **Vercel**).
- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings (Hosted on **Render**).
- **Database:** Managed PostgreSQL (Hosted on **Supabase**).
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic.
- **Database Driver:** Psycopg 3 (`psycopg[binary]`).
- **Configuration:** Environment variables (`.env`).

---

## 3. Project Folder Structure

```text
smart-queue/
│
├── backend/
│   ├── alembic/                     # Alembic migration environment
│   │   ├── versions/                # Schema migration scripts
│   │   ├── env.py                   # Migration runner reading SQLAlchemy settings
│   │   └── script.py.mako           # Revision template
│   ├── app/
│   │   ├── main.py                  # FastAPI app entry with CORS & Render port binding
│   │   ├── database.py              # SQLAlchemy engine, session pooler & DB ping
│   │   ├── config.py                # Environment configuration settings
│   │   ├── models/
│   │   │   └── __init__.py          # SQLAlchemy base (models in Checkpoint 2)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── health.py            # Pydantic liveness and readiness schemas
│   │   ├── routes/
│   │   │   ├── __init__.py          # API router registry
│   │   │   └── health.py            # /api/health (liveness) & /api/ready (readiness)
│   │   └── services/
│   │       ├── __init__.py
│   │       └── health_service.py    # Health check orchestration logic
│   ├── alembic.ini                  # Alembic CLI configuration
│   ├── test_db_connection.py        # Independent Supabase connection test script
│   ├── requirements.txt             # Backend dependencies
│   ├── .env.example                 # Backend environment variable template
│   └── .gitignore                   # Backend git ignore rules
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx           # Top navigation with live status indicator
│   │   │   ├── Footer.jsx           # Clean healthcare footer
│   │   │   └── StatusIndicator.jsx  # Cloud-ready Connected / Pending DB / Offline card
│   │   ├── pages/
│   │   │   └── LandingPage.jsx      # Hospital landing page & purpose overview
│   │   ├── layouts/
│   │   │   └── MainLayout.jsx       # Layout wrapper
│   │   ├── services/
│   │   │   └── api.js               # Centralized Axios client (health & readiness)
│   │   ├── App.jsx                  # Root router & polling loop
│   │   ├── main.jsx                 # React DOM mount
│   │   └── index.css                # Tailwind directives
│   ├── public/
│   │   └── favicon.svg              # Medical hospital logo icon
│   ├── vercel.json                  # Vercel SPA routing rewrite rules
│   ├── index.html                   # HTML template with Google Fonts (Inter)
│   ├── package.json                 # Node dependencies & build scripts
│   ├── vite.config.js               # Vite configuration (port 5173)
│   ├── tailwind.config.js           # Tailwind theme configuration
│   ├── postcss.config.js            # PostCSS configuration
│   ├── .env.example                 # Frontend environment template
│   └── .gitignore                   # Frontend git ignore rules
│
├── database/
│   ├── README.md                    # Detailed Supabase & Alembic documentation
│   └── init_db.sql                  # Standalone SQL initialization script
│
├── docs/
│   └── project-overview.md          # Architecture vision & checkpoint roadmap
│
├── render.yaml                      # Render Blueprint deployment configuration
├── .gitignore                       # Repository-wide ignore rules
└── README.md                        # Master setup & execution guide
```

---

## 4. Prerequisites

- **Python (v3.10+)**: Verify with `python --version`
- **Node.js (v18+ or v20+) and npm**: Verify with `node -v` and `npm -v`
- **Git**: Verify with `git --version`
- **Supabase Account**: Free account at [supabase.com](https://supabase.com)
- **Render Account**: Free account at [render.com](https://render.com)
- **Vercel Account**: Free account at [vercel.com](https://vercel.com)

---

## 5. Supabase Database Setup Instructions

1. Log into [supabase.com](https://supabase.com) and click **New Project**.
2. Set **Project Name** to `smart-queue-hospital` (or your preferred name).
3. Choose a strong **Database Password** and save it.
4. Select a region close to your Render deployment (e.g., `us-east-1` or `us-west-1`).
5. Click **Create new project** and wait ~2 minutes for provisioning.

### Where to Find the Supabase Session Pooler Connection String:
1. In your Supabase dashboard, navigate to **Project Settings** (gear icon) -> **Database**.
2. Scroll to the **Connection string** section.
3. Select the **URI** tab.
4. Select **Session Mode** (port `6543`):
   ```text
   postgresql://postgres.[project-ref]:[your-password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```

---

## 6. Configuring `DATABASE_URL` and Enabling SSL

In `backend/.env`:
```env
# Convert scheme to postgresql+psycopg:// and append ?sslmode=require
DATABASE_URL="postgresql+psycopg://postgres.[project-ref]:your_supabase_password@aws-0-[region].pooler.supabase.com:6543/postgres?sslmode=require"
```

> **Note on SSL:** Supabase requires SSL encryption. Adding `?sslmode=require` ensures all connections over the public internet are encrypted with TLS.

---

## 7. Local Backend Setup and Execution

Open Windows PowerShell:

```powershell
cd "d:\CreatED\queue system\smart-queue\backend"

# 1. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create .env file
Copy-Item .env.example .env
```

Open `backend/.env` and paste your Supabase `DATABASE_URL`.

### Test the Supabase Connection Independently:
```powershell
python test_db_connection.py
```
*Expected output: `[SUCCESS] Connection established successfully to Supabase!`*

### Run the FastAPI Backend:
```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Liveness Probe: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)
- Readiness Probe: [http://127.0.0.1:8000/api/ready](http://127.0.0.1:8000/api/ready)

---

## 8. Alembic Database Migrations

Alembic manages database schema evolution directly against Supabase.

Run inside `backend/` with `(venv)` activated:

```powershell
# Check current migration revision
alembic current

# Generate a migration (when models are added in Checkpoint 2)
alembic revision --autogenerate -m "initial_tables"

# Apply pending migrations to Supabase
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 9. Local Frontend Setup and Execution

Open a **second** Windows PowerShell terminal:

```powershell
cd "d:\CreatED\queue system\smart-queue\frontend"

# 1. Create .env from template
Copy-Item .env.example .env

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser. The landing page will display the real-time status of your Render backend and Supabase database.

---

## 10. Deploying Backend to Render

1. Push your repository to GitHub.
2. Log into [render.com](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Configure service settings:
   - **Name:** `smart-queue-backend`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/api/health`
5. Under **Environment Variables**, add:
   - `APP_ENV`: `production`
   - `DEBUG`: `false`
   - `DATABASE_URL`: *(Your Supabase connection string with `?sslmode=require`)*
   - `FRONTEND_URL`: `https://your-frontend-project.vercel.app`
   - `CORS_ORIGINS`: `https://your-frontend-project.vercel.app`
6. Click **Create Web Service**.
7. Once deployed, note your Render backend URL (e.g., `https://smart-queue-backend.onrender.com`).

---

## 11. Deploying Frontend to Vercel

1. Log into [vercel.com](https://vercel.com) and click **Add New...** -> **Project**.
2. Import your GitHub repository.
3. Configure project settings:
   - **Root Directory:** Edit and select `frontend`.
   - **Framework Preset:** `Vite`.
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
4. Under **Environment Variables**, add:
   - `VITE_API_BASE_URL`: `https://smart-queue-backend.onrender.com` *(Your Render backend URL)*
5. Click **Deploy**.
6. The `frontend/vercel.json` file ensures that all React Router routes route correctly to `index.html`.

---

## 12. Environment Variable Reference for Both Platforms

### Backend Environment Variables (Render & Local `backend/.env`)

| Variable | Description | Local Dev Value | Render (Production) Value |
|---|---|---|---|
| `APP_ENV` | Application environment | `development` | `production` |
| `DEBUG` | FastAPI debug mode | `True` | `False` |
| `HOST` | Server host binding | `127.0.0.1` | `0.0.0.0` |
| `PORT` | Listening port | `8000` | Auto-assigned by Render (`$PORT`) |
| `DATABASE_URL` | Supabase Session Pooler URI | `postgresql+psycopg://...` | `postgresql+psycopg://...` |
| `FRONTEND_URL` | Frontend origin for CORS | `http://localhost:5173` | `https://your-app.vercel.app` |
| `CORS_ORIGINS` | Permitted CORS origins | `http://localhost:5173` | `https://your-app.vercel.app` |

### Frontend Environment Variables (Vercel & Local `frontend/.env`)

| Variable | Description | Local Dev Value | Vercel (Production) Value |
|---|---|---|---|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` | `https://smart-queue-backend.onrender.com` |

---

## 13. Verification & Health Probes

### 1. Liveness Probe (`GET /api/health`):
Indicates that the FastAPI web service process is active.
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/health" | ConvertTo-Json
```
Response:
```json
{
  "application": "The Cost of Waiting - Smart Queuing for Public Hospitals",
  "environment": "development",
  "api": "online",
  "database": {
    "status": "connected",
    "message": "Supabase PostgreSQL connection active and responsive."
  },
  "timestamp": "2026-11-10T16:00:00Z"
}
```

### 2. Readiness Probe (`GET /api/ready`):
Indicates that the backend is ready to accept user requests and Supabase database connectivity has been validated.
- **HTTP 200 OK:** Database connected.
- **HTTP 503 Service Unavailable:** Database unreachable or unconfigured.

---

## 14. How to Upload to GitHub

```powershell
cd "d:\CreatED\queue system\smart-queue"

# Check status to ensure .env is not tracked
git status

# Stage updated cloud architecture files
git add .

# Commit updates
git commit -m "feat(cloud): update architecture to Vercel, Render, Supabase with Alembic migrations"

# Push to GitHub
git push -u origin main
```
