# ICH IT Support Ticketing System

> Internal IT helpdesk system for ICH — built with Python/Flask, SQLAlchemy, and Jinja2 templates.

---

## Features

- Role-based access control (Admin, ICT Officer, Technician, Intern, Staff)
- Asset Register (CRUD for Admins, View/Add for others)
- Ticket creation, assignment, status tracking, and comments
- Admin dashboards with live charts (status, priority, office breakdown, 7-day trend)
- Intern/Technician performance reporting with date filtering
- Printable reports with signature block
- User management — add, suspend, deactivate, reset passwords
- Brute-force login protection, session security, input sanitization

## Getting Started

### For Windows Users
1. Download the repository.
2. Locate `run_windows.bat` in the project root.
3. Double-click `run_windows.bat`. This will automatically set up a virtual environment, install dependencies, and launch the production server.

### For Linux/macOS Users
```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment variables
cp .env.example .env
# Edit .env with your secrets

# 4. Initialize database migrations
flask db upgrade

# 5. Run the production server
python run_production.py
```

The app will be available at `http://localhost:8080` (or the next available port).

**Default admin credentials:**
- Username: `admin`
- Password: `SystemAdm2n`

> ⚠️ Change the admin password immediately after first login.

## Roles

| Role | Create Tickets | Assign | Manage Users | Asset CRUD |
|---|---|---|---|---|
| ADMIN | ✅ | ✅ | ✅ | ✅ |
| ICT_OFFICER | ❌ | ✅ | ❌ | ❌ |
| TECHNICIAN | ❌ | ❌ | ❌ | ❌ |
| INTERN | ❌ | ❌ | ❌ | ❌ |
| STAFF | ✅ | ❌ | ❌ | ❌ |

## Tech Stack

- **Backend**: Python 3, Flask, Flask-Login, SQLAlchemy, Flask-Migrate, Waitress (Production Server)
- **Database**: SQLite / PostgreSQL / MySQL
- **Frontend**: Jinja2, Tailwind CSS (CDN), Chart.js, Hugeicons
- **Auth**: Werkzeug password hashing (scrypt)

## Project Structure

```
├── app.py              # Main application factory & routes
├── models.py           # Database models
├── seed.py             # Development data seeder
├── run_production.py   # Production WSGI runner (Waitress)
├── run_windows.bat     # Windows production launcher
├── requirements.txt    # Python dependencies
├── static/             # Images
├── templates/          # Jinja2 templates
└── migrations/         # Alembic database migrations
```
