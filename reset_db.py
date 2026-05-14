"""
reset_db.py — Wipes all ticket/user/comment data and seeds a clean admin account.
Run once before the pilot: python reset_db.py
"""
from app import app
from models import db, User, Office, Ticket, Comment, ActivityLog
from werkzeug.security import generate_password_hash

ADMIN_EMAIL    = 'admin@ticketing.local'
ADMIN_NAME     = 'System Admin'
ADMIN_PASSWORD = 'SystemAdm2n'

with app.app_context():
    print("Clearing existing data...")

    # Delete in dependency order to avoid FK violations
    ActivityLog.query.delete()
    Comment.query.delete()
    Ticket.query.delete()
    User.query.delete()
    db.session.commit()
    print("  ✓ All tickets, comments, activity logs, and users removed.")

    # Keep offices or recreate them if empty
    if Office.query.count() == 0:
        for name in ['Accounts', 'HR', 'PMU', 'Secretaries', 'ICT']:
            db.session.add(Office(name=name))
        db.session.commit()
        print("  ✓ Default offices created.")
    else:
        print("  ✓ Offices kept intact.")

    # Create clean admin
    ict_office = Office.query.filter_by(name='ICT').first()
    admin = User(
        username='admin',
        password_hash=generate_password_hash(ADMIN_PASSWORD),
        displayName=ADMIN_NAME,
        role='ADMIN',
        officeId=ict_office.id
    )
    db.session.add(admin)
    db.session.commit()

    print(f"\n  ✓ Admin account created.")
    print(f"    Username: admin")
    print(f"    Password: {ADMIN_PASSWORD}")
    print(f"    Role    : ADMIN\n")
    print("Database reset complete. The system is ready for the pilot.")
