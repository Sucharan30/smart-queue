# The Cost of Waiting – Smart Queuing for Public Hospitals

## 1. Project Background & Problem Statement

Public hospital out-patient departments (OPDs) in developing and semi-urban communities face chronic crowding, long wait times, and extreme uncertainty. Patients routinely spend between 3 and 7 hours in hospital waiting halls without knowing:
- How many patients are ahead of them
- When the doctor will attend to their case
- Whether delays or emergencies have paused consultations

### The Hidden Costs of Waiting
1. **Economic Cost & Lost Wages:** Most public hospital attendees are daily-wage earners or low-income workers. An unmanaged hospital queue forces them to sacrifice an entire day's earnings.
2. **Cross-Infection Vulnerability:** Crowded, poorly ventilated waiting rooms exacerbate airborne and droplet transmission among vulnerable patients, children, and elderly individuals.
3. **Psychological & Physical Stress:** Lack of visibility into queue progression leads to anxiety, patient-staff altercations, and patient fatigue.
4. **Healthcare Worker Burnout:** Nurses and administrative staff expend high energy repeatedly addressing "When is my turn?" queries rather than delivering clinical care.

---

## 2. Solution Concept: Smart Queuing via WhatsApp

**The Cost of Waiting** is an intelligent, low-barrier queue management platform tailored for public healthcare facilities. 

Rather than requiring patients to download heavy native smartphone apps or navigate complex portals, the system leverages ubiquitous **WhatsApp messaging**:
- Patients obtain a digital queue token on arrival (or via reception).
- Patients receive immediate confirmation with a unique token code and a secure tracking link.
- Patients monitor live queue progression remotely from outside crowded waiting areas (nearby parks, cafeterias, transit points).
- Automated SMS / WhatsApp alerts notify patients when their turn is within 2-3 consultations (e.g., "Your turn is approaching in ~15 minutes. Please proceed to Clinic 1").

---

## 3. Final Cloud Architecture

The system utilizes a secure, decoupled, cloud-first architecture designed for zero local server maintenance:

```
┌────────────────────────────────────────────────────────┐
│             Frontend (Hosted on Vercel)                │
│  - React.js 18 + Vite + Tailwind CSS                   │
│  - Single Page Application with client-side routing    │
│  - Centralized Axios client targeting Render backend   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTPS REST API requests
┌───────────────────────────▼────────────────────────────┐
│             Backend (Hosted on Render)                 │
│  - Python 3.10+ with FastAPI & Uvicorn ASGI            │
│  - Strict CORS origin whitelisting (Vercel domain)     │
│  - Liveness (/api/health) & Readiness (/api/ready)     │
│  - Alembic automated database migration pipeline       │
└───────────────────────────┬────────────────────────────┘
                            │ Encrypted TLS/SSL Connection (Psycopg 3)
                            │ via Session Pooler (Port 6543)
┌───────────────────────────▼────────────────────────────┐
│             Database (Supabase PostgreSQL)             │
│  - Managed PostgreSQL instance with connection pooling │
│  - High-availability, scalable relational storage     │
└────────────────────────────────────────────────────────┘
```

> **Strict Boundary:** The React frontend **never** connects directly to PostgreSQL or Supabase. All database queries, business rules, and validation are executed by FastAPI.

---

## 4. Checkpoint Development Roadmap

| Checkpoint | Scope | Description |
|---|---|---|
| **Checkpoint 1 (Current)** | **Cloud Architecture & Foundation** | React + Vite on Vercel, FastAPI on Render, Supabase managed PostgreSQL, Alembic migrations, Liveness (`/api/health`), Readiness (`/api/ready`), and live UI status indicator. |
| **Checkpoint 2** | **Core Queuing Engine** | SQLAlchemy models (Clinics, Doctors, Patients, Queue Tickets), Alembic schema migration, ticket generation, status transitions (`waiting`, `in-consultation`, `completed`, `cancelled`). |
| **Checkpoint 3** | **WhatsApp & Notification Integration** | WhatsApp message dispatch and tracking links via webhook / mock provider. |
| **Checkpoint 4** | **Doctor & Staff Dashboard** | Receptionist ticket dispenser and doctor consultation controls ("Call Next", "Pause Queue", "Mark Completed"). |
| **Checkpoint 5** | **Dynamic ETA & Economic Metrics** | Queue waiting time estimation algorithm and economic cost calculation (hours saved, wage loss averted). |

---

## 5. Security & Privacy Principles
- **No PII Exposure:** Queue displays and public endpoints only expose anonymized token identifiers (e.g., `A-014`).
- **No Secret Leakage:** Database credentials and internal error traces are kept strictly within server-side environment variables and never surfaced to the browser or public API responses.
- **Strict CORS Protection:** Wildcard origins (`*`) are disallowed in production environments.
