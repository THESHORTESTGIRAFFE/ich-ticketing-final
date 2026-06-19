from app import app, db
from models import User, Office, Ticket, Comment, ActivityLog
from werkzeug.security import generate_password_hash
import argparse
import random
from datetime import datetime, timedelta, timezone

ADJECTIVES = ['Broken', 'Frozen', 'Slow', 'Missing', 'Urgent', 'Confusing', 'Outdated', 'Loud', 'Sparking', 'Unresponsive']
NOUNS = ['Monitor', 'Printer', 'Software', 'Network', 'Mouse', 'Keyboard', 'Email', 'Server', 'Application', 'Router']
STATUSES = ['OPEN', 'IN_PROGRESS', 'PENDING', 'RESOLVED', 'CLOSED']
PRIORITIES = ['LOW', 'MEDIUM', 'HIGH']
COMMENT_PHRASES = [
    'I will look into this right away.',
    'Please provide more details on the problem.',
    'This appears to be a configuration issue.',
    'I have escalated this to the senior team.',
    'The issue has been resolved, please verify on your end.'
]
ACTIVITY_ACTIONS = [
    'Assigned ticket',
    'Updated ticket details',
    'Added comment',
    'Changed priority',
    'Status updated'
]


def generate_random_date(start_days_ago=90):
    now = datetime.now(timezone.utc)
    random_days = random.randint(0, start_days_ago)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    return now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)


def generate_ticket_id(prefix, created_at, counter):
    dt_str = created_at.strftime('%d%m%y%H%M')
    return f"{prefix}{dt_str}{counter:03d}"


def new_user(username, display_name, role, office_id, password='password'):
    return User(
        username=username,
        password_hash=generate_password_hash(password),
        displayName=display_name,
        role=role,
        officeId=office_id
    )


def seed_database(total_tickets=80):
    with app.app_context():
        offices = Office.query.all()
        if not offices:
            for name in ['Accounts', 'HR', 'PMU', 'Secretaries', 'ICT']:
                db.session.add(Office(name=name))
            db.session.commit()
            offices = Office.query.all()

        if User.query.filter_by(username='staff1').first():
            print('Database already contains seed data.')
            return

        print('Seeding dummy data...')

        ict_office = next((o for o in offices if o.name == 'ICT'), offices[0])
        non_ict_offices = [o for o in offices if o.name != 'ICT']

        users = []
        staff_members = []
        techs = []
        interns = []

        for i in range(1, 5):
            intern = new_user(
                f'intern{i}',
                f'Junior Intern {i}',
                'INTERN',
                ict_office.id
            )
            db.session.add(intern)
            interns.append(intern)
            users.append(intern)

        for i in range(1, 5):
            tech = new_user(
                f'tech{i}',
                f'Senior Tech {i}',
                'TECHNICIAN',
                ict_office.id
            )
            db.session.add(tech)
            techs.append(tech)
            users.append(tech)

        for i in range(1, 16):
            office = random.choice(non_ict_offices)
            staff = new_user(
                f'staff{i}',
                f'Staff User {i}',
                'STAFF',
                office.id
            )
            db.session.add(staff)
            staff_members.append(staff)
            users.append(staff)

        if not User.query.filter_by(username='admin').first():
            admin = new_user(
                'admin',
                'System Admin',
                'ADMIN',
                ict_office.id,
                password='SystemAdm2n'
            )
            db.session.add(admin)
            users.append(admin)

        db.session.commit()

        total_tickets = 80
        ticket_counter = 1

        for _ in range(total_tickets):
            creator = random.choice(staff_members)
            assignee = random.choice(techs + interns) if random.random() > 0.25 else None
            status = random.choice(STATUSES) if assignee else 'OPEN'
            created_at = generate_random_date()

            responded_at = None
            resolved_at = None

            if assignee:
                responded_at = created_at + timedelta(minutes=random.randint(10, 1440))

            if status in ['RESOLVED', 'CLOSED'] and responded_at:
                resolved_at = responded_at + timedelta(hours=random.randint(1, 72))

            prefix = creator.office.name[:3].lower() if creator.office else 'sys'
            ticket_id = generate_ticket_id(prefix, created_at, ticket_counter)
            ticket_counter += 1

            ticket = Ticket(
                id=ticket_id,
                title=f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)} Issue",
                description=(
                    f"Hello IT, I am experiencing issues with my {random.choice(NOUNS).lower()}. "
                    f"The system appears to be {random.choice(ADJECTIVES).lower()} and requires assistance."
                ),
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

            if assignee:
                db.session.add(ActivityLog(
                    ticketId=ticket_id,
                    userId=assignee.id,
                    action='Assigned ticket',
                    details=f'Assigned to {assignee.displayName}',
                    createdAt=responded_at or created_at
                ))

            if random.random() > 0.4:
                comment_author = assignee or creator
                comment_time = responded_at or created_at + timedelta(minutes=15)
                db.session.add(Comment(
                    ticketId=ticket_id,
                    authorId=comment_author.id,
                    content=random.choice(COMMENT_PHRASES),
                    createdAt=comment_time
                ))
                db.session.add(ActivityLog(
                    ticketId=ticket_id,
                    userId=comment_author.id,
                    action='Added comment',
                    details=random.choice(COMMENT_PHRASES),
                    createdAt=comment_time
                ))

            if resolved_at:
                db.session.add(ActivityLog(
                    ticketId=ticket_id,
                    userId=assignee.id,
                    action=f'Status changed to {status}',
                    createdAt=resolved_at
                ))

        db.session.commit()
        print(f"Successfully injected {total_tickets} fake tickets, {len(techs)} tech/intern users, and {len(staff_members)} staff users.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seed the ticketing database with test data.')
    parser.add_argument(
        '--tickets', '-t',
        type=int,
        default=80,
        help='Number of fake tickets to create (default: 80)'
    )
    args = parser.parse_args()
    seed_database(total_tickets=args.tickets)
