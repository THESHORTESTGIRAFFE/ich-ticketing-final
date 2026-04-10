from app import app, db
from models import User, Office, Ticket, Comment, ActivityLog
from werkzeug.security import generate_password_hash
import random
import string
from datetime import datetime, timedelta, timezone

ADJECTIVES = ['Broken', 'Frozen', 'Slow', 'Missing', 'Urgent', 'Confusing', 'Outdated', 'Loud', 'Sparking', 'Unresponsive']
NOUNS = ['Monitor', 'Printer', 'Software', 'Network', 'Mouse', 'Keyboard', 'Email', 'Server', 'Application', 'Router']
STATUSES = ['OPEN', 'IN_PROGRESS', 'PENDING', 'RESOLVED', 'CLOSED']
PRIORITIES = ['LOW', 'MEDIUM', 'HIGH']

def generate_random_date(start_days_ago=30):
    now = datetime.now(timezone.utc)
    random_days = random.randint(0, start_days_ago)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    return now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)

def seed_database():
    with app.app_context():
        # Assume init_db.py or app.py already created core offices
        offices = Office.query.all()
        if not offices:
            for name in ['Accounts', 'HR', 'PMU', 'Secretaries', 'ICT']:
                db.session.add(Office(name=name))
            db.session.commit()
            offices = Office.query.all()

        # Check if we already have seeded data
        if User.query.filter_by(email='intern1@ticketing.local').first():
            print("Database already contains seed data.")
            return

        print("Seeding dummy data...")

        # Create dummy Interns and Techs
        ict_office = next((o for o in offices if o.name == 'ICT'), offices[0])
        techs = []
        for i in range(1, 4):
            tech = User(
                email=f'intern{i}@ticketing.local',
                password_hash=generate_password_hash('password'),
                displayName=f'Junior Intern {i}',
                role='INTERN',
                officeId=ict_office.id
            )
            db.session.add(tech)
            techs.append(tech)

        for i in range(1, 3):
            tech = User(
                email=f'tech{i}@ticketing.local',
                password_hash=generate_password_hash('password'),
                displayName=f'Senior Tech {i}',
                role='TECHNICIAN',
                officeId=ict_office.id
            )
            db.session.add(tech)
            techs.append(tech)

        # Create dummy Staff
        staff_members = []
        for i in range(1, 10):
            office = random.choice([o for o in offices if o.name != 'ICT'])
            staff = User(
                email=f'staff{i}@ticketing.local',
                password_hash=generate_password_hash('password'),
                displayName=f'Staff User {i}',
                role='STAFF',
                officeId=office.id
            )
            db.session.add(staff)
            staff_members.append(staff)

        db.session.commit()

        # Define time range
        now = datetime.now(timezone.utc)

        # Create 50 dummy tickets
        for i in range(50):
            creator = random.choice(staff_members)
            assignee = random.choice(techs) if random.random() > 0.3 else None
            status = random.choice(STATUSES) if assignee else 'OPEN'
            
            created_at = generate_random_date()
            
            # Mock resolved/responded logic logically flowing from created_at
            responded_at = None
            resolved_at = None
            
            if assignee:
                responded_at = created_at + timedelta(minutes=random.randint(5, 2880)) # 5 mins to 2 days
                
            if status in ['RESOLVED', 'CLOSED'] and responded_at:
                resolved_at = responded_at + timedelta(hours=random.randint(1, 72))

            # custom ticket ID generation
            prefix = creator.office.name[:3].lower() if creator.office else "sys"
            dt_str = created_at.strftime('%d%m%y%H%M')
            
            # small offset locally to guarantee seed uniqueness without changing visual format
            created_at = created_at + timedelta(minutes=1)
            ticket_id = f"{prefix}{dt_str}"

            ticket = Ticket(
                id=ticket_id,
                title=f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} Issue",
                description=f"Hello IT, I am experiencing issues with my system. It seems the {random.choice(NOUNS).lower()} is {random.choice(ADJECTIVES).lower()}.",
                officeId=creator.officeId,
                createdBy=creator.id,
                assignedTo=assignee.id if assignee else None,
                status=status,
                priority=random.choice(PRIORITIES),
                createdAt=created_at,
                updatedAt=resolved_at or responded_at or created_at,
                respondedAt=responded_at,
                resolvedAt=resolved_at
            )
            db.session.add(ticket)
            db.session.commit() # commit to get ticket.id
            
            # Add some dummy comments
            if assignee and random.random() > 0.5:
                comment = Comment(
                    ticketId=ticket.id,
                    authorId=assignee.id,
                    content="I will look into this right away.",
                    createdAt=responded_at
                )
                db.session.add(comment)
                db.session.add(ActivityLog(ticketId=ticket.id, userId=assignee.id, action='Added Comment', createdAt=responded_at))
            
            if resolved_at:
                db.session.add(ActivityLog(ticketId=ticket.id, userId=assignee.id, action=f'Status changed to {status}', createdAt=resolved_at))

        db.session.commit()
        print("Successfully injected 50 fake tickets, 5 tech staff, and 9 standard staff.")

if __name__ == '__main__':
    seed_database()
