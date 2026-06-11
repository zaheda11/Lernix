# LERNIX — AI Curriculum Planner

> An AI-powered academic curriculum generation and student learning management platform built with Flask and a locally hosted LLM (Ollama / IBM Granite).

**Author:** [Sindhura Karumuri](https://github.com/Sindhura-Karumuri)
**Repository:** https://github.com/Sindhura-Karumuri/Lernix

---

## Overview

LERNIX enables educators to generate fully structured, multi-semester academic curricula in seconds using AI. Students can enrol into published curricula, receive personalized weekly study plans, take AI-generated quizzes, track task-level progress, and get course-specific interview preparation — all within a single platform.

Three distinct user roles drive the experience:
- **Educator** — generates and manages AI curricula, monitors student engagement via a tracker
- **Student** — browses and enrols in curricula, follows study plans, takes quizzes, tracks progress
- **Admin** — full system visibility: users, curricula, feedback, download analytics

---

## Features

- AI curriculum generation (title, field, semesters, audience → full structured curriculum)
- Semester-wise course breakdown with codes, credits, outcomes, prerequisites, assessments, and resources
- Visual curriculum roadmap
- Student opt-in / opt-out enrolment
- AI-generated personalized weekly study plans per course
- Task-level checkbox progress tracking (persisted per student)
- AI quiz generation — course-level and semester-level — with score logging and wrong-answer explanations
- AI assistant for course-specific Q&A and interview preparation
- Multi-format export: PDF, DOCX, JSON, CSV
- AI-powered standalone academic report generator
- Admin dashboard: system stats, user management, curriculum list, feedback, download analytics
- Subscription tiers: Free (5 generations/month), Monthly, Annual
- Role-based access control with session authentication
- Password reset and profile management

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 / Flask 3.x |
| Database | SQLite (default), upgradeable to PostgreSQL |
| AI / LLM | Ollama (local) — IBM Granite model |
| PDF Export | ReportLab 4.x |
| DOCX Export | python-docx 1.x |
| Frontend | Jinja2 templates, vanilla JavaScript, CSS |
| Server | Gunicorn (production) |

---

## Project Structure

```
lernix/
├── app.py                  # All Flask routes and API endpoints
├── database.py             # SQLite CRUD operations and schema migration
├── llm_service.py          # Ollama LLM prompt construction and API calls
├── pdf_generator.py        # PDF, DOCX, and TXT report generation
├── schema.sql              # Full database schema (8 tables)
├── requirements.txt        # Python dependencies
├── Procfile                # Gunicorn start command for cloud deployment
├── runtime.txt             # Python version pin (3.11.9)
├── .env.example            # Environment variable template
├── static/
│   ├── css/
│   │   └── style.css       # Global stylesheet
│   └── js/
│       ├── main.js         # Core interactions: auth, quiz, assistant, opt-in
│       ├── dashboard.js    # Dashboard dynamic elements
│       └── roadmap.js      # Visual curriculum roadmap renderer
└── templates/
    ├── base.html           # Shared layout (nav, flash messages, footer)
    ├── login.html          # Login and registration
    ├── dashboard.html      # Student / Educator dashboard
    ├── admin_dashboard.html# Admin panel
    ├── generate.html       # Curriculum generation form
    ├── curriculum.html     # Curriculum detail view
    ├── roadmap.html        # Visual roadmap
    ├── assistant.html      # AI study plan + interview prep
    ├── assistant_plan.html # Weekly task checklist
    ├── history.html        # Curriculum history + downloads
    ├── tracker.html        # Educator student tracker
    ├── profile.html        # Profile management
    ├── subscription.html   # Subscription tier management
    ├── feedback.html       # Platform feedback
    ├── faq.html            # FAQ page
    ├── contact.html        # Contact page
    └── forgot_password.html# Password reset
```

---

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed and running locally
- IBM Granite model pulled in Ollama:

```bash
ollama pull granite3.1-dense:2b
```

> Any Ollama-compatible model works. Update the model name in `llm_service.py` if using a different one.

---

## Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Sindhura-Karumuri/Lernix.git
cd Lernix

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Open .env and set SECRET_KEY to a strong random value

# 5. Start Ollama (in a separate terminal)
ollama serve

# 6. Run the application
flask run
```

Open `http://localhost:5000` in your browser.

---

## Default Accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@lernix.edu | admin123 |
| Educator | educator@lernix.edu | educator123 |
| Student | student@lernix.edu | student123 |

> Change all default passwords before any public or production deployment.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session signing key | auto-generated (insecure) |
| `FLASK_DEBUG` | Enable debug mode (`1` / `0`) | `0` |
| `DATABASE_PATH` | Path to the SQLite database file | `lernix.db` |
| `OLLAMA_BASE_URL` | Ollama API base URL | `http://localhost:11434` |

Copy `.env.example` to `.env` and fill in values before running.

---

## API Endpoints

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/api/auth/login` | Public | Authenticate and start session |
| POST | `/api/auth/register` | Public | Create new account |
| POST | `/api/auth/forgot_password` | Public | Reset password by email |
| POST | `/api/generate` | Educator / Admin | Generate AI curriculum |
| GET | `/api/curriculum/<id>` | Any | Fetch curriculum JSON |
| GET | `/api/curriculum/<id>/courses` | Any | List course names |
| POST | `/api/curriculum/optin` | Student | Enrol in curriculum |
| POST | `/api/curriculum/optout` | Student | Remove enrolment |
| POST | `/api/curriculum/<id>/rate` | Any | Rate a curriculum (1–5) |
| POST | `/api/curriculum/delete/<id>` | Educator / Admin | Delete curriculum |
| POST | `/api/assistant/generate` | Any | Generate AI study plan |
| POST | `/api/assistant/task/toggle` | Student | Toggle task completion |
| POST | `/api/assistant/interview/ask` | Any | Get AI interview answer |
| GET | `/api/quiz/get` | Any | Fetch AI-generated quiz questions |
| POST | `/api/quiz/submit` | Student | Submit quiz score |
| POST | `/api/feedback` | Any | Submit platform feedback |
| POST | `/api/profile/update` | Any | Update profile details |
| POST | `/api/subscription/upgrade` | Any | Change subscription tier |
| POST | `/api/report/generate` | Any | Generate full AI report (PDF/DOCX/TXT) |

---

## Export Formats

| Route | Format | Description |
|---|---|---|
| `/curriculum/<id>/export/pdf` | PDF | Formatted curriculum document |
| `/curriculum/<id>/export/json` | JSON | Machine-readable curriculum data |
| `/curriculum/<id>/export/csv` | CSV | Spreadsheet-compatible course list |
| `/api/report/generate` | PDF / DOCX / TXT | Full AI-generated academic report |

---

## Deployment (Render / Railway / Heroku)

1. Push to GitHub
2. Create a new Web Service on your chosen platform
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Add environment variables:
   - `SECRET_KEY` — a long random string (use `python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FLASK_DEBUG` — `0`
   - `DATABASE_PATH` — `lernix.db` or a persistent volume path
   - `OLLAMA_BASE_URL` — URL of your hosted Ollama instance

> SQLite is suitable for demos and single-instance deployments. For production traffic with concurrent users, migrate to PostgreSQL — no application-level changes are required beyond updating the database connection in `database.py`.

---

## Database

The schema is defined in `schema.sql` and auto-applied on first run via `database.init_db()`. Subsequent runs apply migration patches without dropping existing data.

**Tables:**

| Table | Purpose |
|---|---|
| `users` | All users — students, educators, admins |
| `curricula` | AI-generated curriculum records |
| `student_curricula` | Student enrolment (opt-in) linkage |
| `learning_plans` | AI-generated weekly study plans |
| `student_tasks` | Per-task checkbox progress |
| `student_quizzes` | Quiz attempt scores and explanations |
| `download_history` | Export action logs |
| `feedbacks` | Platform feedback and ratings |

---

## License

This project is for academic and educational use.
