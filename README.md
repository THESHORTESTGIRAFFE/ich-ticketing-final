# ICH IT Support Ticketing System

> Internal IT helpdesk system for ICH — built with Python/Flask, SQLAlchemy, and Jinja2 templates.

---

## Features

- Role-based access control (Admin, ICT Officer, Technician, Intern, Staff)
- Ticket creation, assignment, status tracking, and comments
- Admin dashboards with live charts (status, priority, office breakdown, 7-day trend)
- Intern/Technician performance reporting with date filtering
- Printable reports with signature block
- User management — add, suspend, deactivate, reset passwords
- Brute-force login protection, session security, input sanitization

## Quick Start

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Set environment variables for MySQL
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="mysql+pymysql://user:pass@localhost/ich_ticketing"

# 4. Run the application (auto-creates DB and seeds default data)
python app.py
```

The app will be available at `http://localhost:5000`

**Default admin credentials:**
- Email: `admin@ticketing.local`
- Password: `password`

> ⚠️ Change the admin password immediately after first login.

## Roles

| Role | Can Create Tickets | Can Assign | Can Manage Users | Dashboard |
|---|---|---|---|---|
| ADMIN | ✅ | ✅ | ✅ | Charts + all data |
| ICT_OFFICER | ❌ | ✅ | ❌ | Unassigned ticket queue |
| TECHNICIAN | ❌ | ❌ | ❌ | Assigned tickets |
| INTERN | ❌ | ❌ | ❌ | Assigned tickets |
| STAFF | ✅ | ❌ | ❌ | Own tickets only |

## Tech Stack

- **Backend**: Python 3, Flask, Flask-Login, SQLAlchemy
- **Database**: SQLite (dev) / MySQL (production)
- **Frontend**: Jinja2 templates, Tailwind CSS (CDN), Chart.js, DataTables.js
- **Auth**: Werkzeug password hashing (scrypt)

## Project Structure

```
├── app.py              # Main application — all routes and business logic
├── models.py           # Database models (User, Office, Ticket, Comment, ActivityLog)
├── seed.py             # Development data seeder (50 dummy tickets)
├── requirements.txt    # Python dependencies
├── static/             # Logo images
├── templates/
│   ├── layout.html         # Base template (navbar, footer)
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── ticket_form.html    # New ticket form
│   ├── ticket_detail.html  # View/comment/update ticket
│   ├── admin_users.html    # User management
│   ├── admin_offices.html  # Office management
│   ├── admin_tickets.html  # All tickets table
│   ├── admin_report.html   # Performance report (printable)
│   └── dashboards/
│       ├── admin.html
│       ├── ict.html
│       ├── technician.html
│       └── staff.html
```

## Production Deployment

```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Run with gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

See [docs/SECURITY.md](docs/SECURITY.md) for the full security checklist.
