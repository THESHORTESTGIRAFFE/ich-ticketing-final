import os
import re
from flask import Flask, render_template, redirect, url_for, flash, request, abort, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import string
import random
from sqlalchemy import func
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask_migrate import Migrate
from models import db, User, Office, Ticket, Comment, ActivityLog

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# ── Security config ──────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-must-be-changed-in-prod')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 28800)))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Database ─────────────────────────────────────────────────────────────────
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ich_ticketing.db')

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

# ── Logging Setup ─────────────────────────────────────────────────────────────
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/ich_ticketing.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('ICH Ticketing startup')

# ── Security headers on every response ───────────────────────────────────────
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# ── Input sanitizer ───────────────────────────────────────────────────────────
def sanitize(value, max_len=255):
    """Strip leading/trailing whitespace, collapse internal whitespace,
    remove common script-injection characters, and enforce a maximum length."""
    if not value:
        return ''
    value = value.strip()
    # Remove null bytes & control characters
    value = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', value)
    return value[:max_len]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = sanitize(request.form.get('email', ''), 255).lower()
        password = request.form.get('password', '')

        # ── Brute-force protection ────────────────────────────────────────────
        now = datetime.now(timezone.utc)
        lockout_until = session.get('lockout_until')
        if lockout_until and now.timestamp() < lockout_until:
            minutes_left = int((lockout_until - now.timestamp()) / 60) + 1
            flash(f'Too many failed attempts. Try again in {minutes_left} minute(s).', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            # ── Reset failed counter on success ──
            session.pop('login_attempts', None)
            session.pop('lockout_until', None)
            if not user.is_active:
                flash('This account has been deactivated. Contact your administrator.', 'danger')
            elif user.is_suspended:
                flash('This account is suspended. Contact your administrator.', 'danger')
            else:
                login_user(user, remember=False)
                session.permanent = True
                next_page = request.args.get('next')
                # Open redirect guard: only allow relative redirects
                if next_page and not next_page.startswith('/'):
                    next_page = None
                flash('Successfully logged in!', 'success')
                return redirect(next_page or url_for('dashboard'))
        else:
            attempts = session.get('login_attempts', 0) + 1
            session['login_attempts'] = attempts
            remaining = max(0, 5 - attempts)
            if attempts >= 5:
                session['lockout_until'] = (now + timedelta(minutes=15)).timestamp()
                session.pop('login_attempts', None)
                flash('Account locked after 5 failed attempts. Try again in 15 minutes.', 'danger')
            else:
                flash(f'Invalid email or password. {remaining} attempt(s) remaining before lockout.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = sanitize(request.form.get('email', ''), 255).lower()
        password = request.form.get('password', '')
        display_name = sanitize(request.form.get('displayName', ''), 100)
        office_id = request.form.get('officeId', '').strip()

        # ── Server-side validation ────────────────────────────────────────────
        errors = []
        if not re.match(r'^[\w.+-]+@[\w-]+\.[\w.]+$', email):
            errors.append('Please enter a valid email address.')
        if len(display_name) < 2:
            errors.append('Full name must be at least 2 characters.')
        if len(password) < 8:
            errors.append('Password must be at least 8 characters.')
        if not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        if not re.search(r'\d', password):
            errors.append('Password must contain at least one number.')
        if not office_id or not Office.query.get(office_id):
            errors.append('Please select a valid office from the list.')
        if User.query.filter_by(email=email).first():
            errors.append('An account with that email already exists.')

        if errors:
            for e in errors:
                flash(e, 'danger')
            return redirect(url_for('register'))

        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            displayName=display_name,
            officeId=office_id,
            role='STAFF'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))

    offices = Office.query.order_by(Office.name).all()
    return render_template('register.html', offices=offices)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'ADMIN':
        stats = {
            'total': Ticket.query.count(),
            'open': Ticket.query.filter_by(status='OPEN').count(),
            'in_progress': Ticket.query.filter_by(status='IN_PROGRESS').count(),
            'resolved': Ticket.query.filter_by(status='RESOLVED').count()
        }
        
        # Aggregation for Charts
        status_counts = dict(db.session.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all())
        priority_counts = dict(db.session.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all())
        office_counts = dict(db.session.query(Office.name, func.count(Ticket.id)).join(Ticket, Office.id == Ticket.officeId).group_by(Office.name).all())
        
        # 7-day trend
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_tickets = Ticket.query.filter(Ticket.createdAt >= seven_days_ago).all()
        dates_dict = {}
        for i in range(7):
            day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime('%b %d')
            dates_dict[day] = 0
            
        for t in recent_tickets:
            day_str = t.createdAt.strftime('%b %d')
            if day_str in dates_dict:
                dates_dict[day_str] += 1
                
        # We need the trend in chronological order (oldest first)
        trend_keys = list(dates_dict.keys())[::-1]
        trend_values = [dates_dict[k] for k in trend_keys]
        
        chart_data = {
            'status': status_counts,
            'priority': priority_counts,
            'office': office_counts,
            'trend_labels': trend_keys,
            'trend_data': trend_values
        }
        
        return render_template('dashboards/admin.html', stats=stats, chart_data=chart_data)
        
    elif current_user.role == 'ICT_OFFICER':
        unassigned = Ticket.query.filter_by(assignedTo=None).order_by(Ticket.createdAt.desc()).all()
        technicians = User.query.filter(User.role.in_(['TECHNICIAN', 'INTERN'])).all()
        return render_template('dashboards/ict.html', tickets=unassigned, technicians=technicians)
        
    elif current_user.role in ['TECHNICIAN', 'INTERN']:
        assigned_query = Ticket.query.filter_by(assignedTo=current_user.id)
        
        # Stats specifically for this technician
        stats = {
            'total': assigned_query.count(),
            'open': assigned_query.filter_by(status='OPEN').count(),
            'in_progress': assigned_query.filter_by(status='IN_PROGRESS').count(),
            'resolved': assigned_query.filter_by(status='RESOLVED').count()
        }
        
        # Chart Data for technician
        status_counts = dict(db.session.query(Ticket.status, func.count(Ticket.id)).filter(Ticket.assignedTo == current_user.id).group_by(Ticket.status).all())
        priority_counts = dict(db.session.query(Ticket.priority, func.count(Ticket.id)).filter(Ticket.assignedTo == current_user.id).group_by(Ticket.priority).all())
        
        # 7-day trend for assigned tickets
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_tickets = assigned_query.filter(Ticket.createdAt >= seven_days_ago).all()
        dates_dict = {}
        for i in range(7):
            day = (datetime.now(timezone.utc) - timedelta(days=i)).strftime('%b %d')
            dates_dict[day] = 0
            
        for t in recent_tickets:
            day_str = t.createdAt.strftime('%b %d')
            if day_str in dates_dict:
                dates_dict[day_str] += 1
                
        trend_keys = list(dates_dict.keys())[::-1]
        trend_values = [dates_dict[k] for k in trend_keys]
        
        chart_data = {
            'status': status_counts,
            'priority': priority_counts,
            'trend_labels': trend_keys,
            'trend_data': trend_values
        }

        return render_template('dashboards/technician.html', 
                               stats=stats,
                               chart_data=chart_data)
        
    else: # STAFF
        my_tickets = Ticket.query.filter_by(createdBy=current_user.id).order_by(Ticket.createdAt.desc()).all()
        return render_template('dashboards/staff.html', tickets=my_tickets)

@app.route('/my-tasks')
@login_required
def my_tasks():
    if current_user.role not in ['TECHNICIAN', 'INTERN']:
        abort(403)
    assigned_tickets = Ticket.query.filter_by(assignedTo=current_user.id).order_by(Ticket.createdAt.desc()).all()
    return render_template('my_tasks.html', tickets=assigned_tickets)

@app.route('/open-pool')
@login_required
def open_pool():
    if current_user.role not in ['TECHNICIAN', 'INTERN']:
        abort(403)
    open_tickets = Ticket.query.filter_by(status='OPEN', assignedTo=None).order_by(Ticket.createdAt.desc()).all()
    return render_template('open_pool.html', tickets=open_tickets)

@app.route('/ticket/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    # Only STAFF and ADMIN can open tickets
    if current_user.role in ['ICT_OFFICER', 'TECHNICIAN', 'INTERN']:
        flash('ICT and Technical staff cannot open tickets.', 'warning')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        title = sanitize(request.form.get('title', ''), 200)
        description = sanitize(request.form.get('description', ''), 2000)
        priority = request.form.get('priority', 'MEDIUM')

        # Validate inputs
        if len(title) < 5:
            flash('Ticket title must be at least 5 characters.', 'danger')
            return render_template('ticket_form.html')
        if priority not in ['LOW', 'MEDIUM', 'HIGH']:
            priority = 'MEDIUM'
        if not current_user.officeId:
            flash('Your account has no office assigned. Contact the administrator.', 'danger')
            return redirect(url_for('dashboard'))
        
        # custom ticket ID generation
        office = Office.query.get(current_user.officeId)
        prefix = office.name[:3].lower() if office else "sys"
        dt_str = datetime.now(timezone.utc).strftime('%d%m%y%H%M')
        ticket_id = f"{prefix}{dt_str}"
        
        ticket = Ticket(
            id=ticket_id,
            title=title,
            description=description,
            priority=priority,
            officeId=current_user.officeId,
            createdBy=current_user.id
        )
        db.session.add(ticket)
        db.session.commit()
        
        # log activity
        log = ActivityLog(ticketId=ticket.id, userId=current_user.id, action='Created Ticket')
        db.session.add(log)
        db.session.commit()
        
        flash('Your ticket has been created!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('ticket_form.html')

@app.route('/ticket/<ticket_id>', methods=['GET'])
@login_required
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    # RBAC checks
    if current_user.role == 'STAFF' and ticket.createdBy != current_user.id:
        abort(403)
        
    comments = Comment.query.filter_by(ticketId=ticket_id).order_by(Comment.createdAt.asc()).all()
    technicians = User.query.filter(User.role.in_(['TECHNICIAN', 'INTERN'])).all()
    
    return render_template('ticket_detail.html', ticket=ticket, comments=comments, technicians=technicians)

@app.route('/ticket/<ticket_id>/action', methods=['POST'])
@login_required
def ticket_action(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    action_type = request.form.get('action_type')

    if action_type == 'comment':
        content = request.form.get('content')
        if content:
            comment = Comment(ticketId=ticket_id, authorId=current_user.id, content=content)
            db.session.add(comment)
            db.session.add(ActivityLog(ticketId=ticket_id, userId=current_user.id, action='Added Comment'))
            
            # Record response time if it hasn't been recorded and user is an intern/tech
            if not ticket.respondedAt and current_user.role in ['INTERN', 'TECHNICIAN']:
                ticket.respondedAt = datetime.now(timezone.utc)
                
            db.session.commit()
            
    elif action_type == 'update_status' and current_user.role != 'STAFF':
        new_status = request.form.get('status')
        old_status = ticket.status
        ticket.status = new_status
        if new_status in ['RESOLVED', 'CLOSED']:
            ticket.resolvedAt = datetime.now(timezone.utc)
        
        # Record response time if a tech/intern updates the status directly without commenting
        if not ticket.respondedAt and current_user.role in ['INTERN', 'TECHNICIAN']:
            ticket.respondedAt = datetime.now(timezone.utc)
            
        db.session.add(ActivityLog(ticketId=ticket_id, userId=current_user.id, action=f'Status changed to {new_status}'))
        db.session.commit()
        
    elif action_type == 'assign':
        if current_user.role in ['ADMIN', 'ICT_OFFICER']:
            tech_id = request.form.get('technician_id')
        elif current_user.role in ['TECHNICIAN', 'INTERN']:
            # Technical staff can ONLY assign to themselves
            tech_id = current_user.id
        else:
            abort(403)

        if tech_id:
            ticket.assignedTo = tech_id
            ticket.status = 'IN_PROGRESS'
            db.session.add(ActivityLog(ticketId=ticket_id, userId=current_user.id, action='Assigned Ticket', details=f"Assigned to {User.query.get(tech_id).displayName}"))
            db.session.commit()
            flash('Ticket assigned successfully.', 'success')
        else:
            flash('No technician selected.', 'danger')

    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    if current_user.role != 'ADMIN':
        abort(403)

    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        user = User.query.get(user_id) if user_id else None

        if action == 'update_role' and user and current_user.id != user.id:
            new_role = request.form.get('role')
            if new_role in ['ADMIN', 'ICT_OFFICER', 'TECHNICIAN', 'INTERN', 'STAFF']:
                user.role = new_role
                db.session.commit()
                flash(f'Role updated for {user.displayName}', 'success')

        elif action == 'suspend' and user and current_user.id != user.id:
            user.is_suspended = True
            db.session.commit()
            flash(f'{user.displayName} has been suspended.', 'warning')

        elif action == 'unsuspend' and user and current_user.id != user.id:
            user.is_suspended = False
            db.session.commit()
            flash(f'{user.displayName} has been unsuspended.', 'success')

        elif action == 'deactivate' and user and current_user.id != user.id:
            user.is_active = False
            db.session.commit()
            flash(f'{user.displayName} has been deactivated.', 'danger')

        elif action == 'activate' and user and current_user.id != user.id:
            user.is_active = True
            db.session.commit()
            flash(f'{user.displayName} has been re-activated.', 'success')

        elif action == 'reset_password' and user and current_user.id != user.id:
            new_pw = request.form.get('new_password')
            if new_pw and len(new_pw) >= 6:
                user.password_hash = generate_password_hash(new_pw)
                db.session.commit()
                flash(f'Password reset for {user.displayName}.', 'success')
            else:
                flash('Password must be at least 6 characters.', 'danger')

        elif action == 'add_user':
            email = request.form.get('new_email')
            name = request.form.get('new_name')
            role = request.form.get('new_role', 'STAFF')
            office_id = request.form.get('new_office_id')
            password = request.form.get('new_password')
            if email and name and password:
                if User.query.filter_by(email=email).first():
                    flash('Email already exists.', 'danger')
                else:
                    new_user = User(
                        email=email,
                        displayName=name,
                        role=role,
                        officeId=office_id or None,
                        password_hash=generate_password_hash(password)
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    flash(f'User {name} created successfully.', 'success')
            else:
                flash('Please fill in all required fields.', 'danger')

        return redirect(url_for('admin_users'))

    users = User.query.order_by(User.displayName).all()
    offices = Office.query.order_by(Office.name).all()
    return render_template('admin_users.html', users=users, offices=offices)

@app.route('/admin/offices', methods=['GET', 'POST'])
@login_required
def admin_offices():
    if current_user.role != 'ADMIN':
        abort(403)
        
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            office = Office(name=name)
            db.session.add(office)
            db.session.commit()
            flash(f'Office {name} added', 'success')
            
    offices = Office.query.all()
    return render_template('admin_offices.html', offices=offices)

@app.route('/admin/tickets')
@login_required
def admin_tickets():
    if current_user.role != 'ADMIN':
        abort(403)
        
    tickets = Ticket.query.order_by(Ticket.createdAt.desc()).all()
    return render_template('admin_tickets.html', tickets=tickets)

@app.route('/admin/report')
@login_required
def admin_report():
    if current_user.role != 'ADMIN':
        abort(403)

    date_from_str = request.args.get('date_from', '')
    date_to_str = request.args.get('date_to', '')

    query = Ticket.query.join(User, Ticket.assignedTo == User.id)\
                .filter(User.role.in_(['INTERN', 'TECHNICIAN']))\
                .order_by(Ticket.createdAt.asc())

    date_from = None
    date_to = None
    if date_from_str:
        try:
            date_from = datetime.strptime(date_from_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            query = query.filter(Ticket.createdAt >= date_from)
        except ValueError:
            pass
    if date_to_str:
        try:
            date_to = datetime.strptime(date_to_str, '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1)
            query = query.filter(Ticket.createdAt < date_to)
        except ValueError:
            pass

    tickets = query.all()

    report_data = []
    total_resolve_hours = 0.0
    resolved_count = 0

    for t in tickets:
        time_to_resolve = "Pending"
        resolve_hours = None
        if t.resolvedAt:
            diff = t.resolvedAt - t.createdAt
            resolve_hours = diff.total_seconds() / 3600
            total_resolve_hours += resolve_hours
            resolved_count += 1
            time_to_resolve = f"{resolve_hours:.1f} hrs"

        report_data.append({
            'ticket': t,
            'time_to_resolve': time_to_resolve,
        })

    avg_resolve = (total_resolve_hours / resolved_count) if resolved_count else 0

    totals = {
        'total': len(report_data),
        'resolved': resolved_count,
        'pending': len(report_data) - resolved_count,
        'total_hours': f"{total_resolve_hours:.1f}",
        'avg_hours': f"{avg_resolve:.1f}",
    }

    return render_template('admin_report.html',
                           report_data=report_data,
                           totals=totals,
                           date_from=date_from_str,
                           date_to=date_to_str,
                           now=datetime.now(timezone.utc),
                           today=datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                           min_date=(datetime.now(timezone.utc) - timedelta(days=365)).strftime('%Y-%m-%d'))

# ── Error Handlers ───────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

def create_db_and_seed():
    with app.app_context():
        # In production, use migrations instead of db.create_all()
        if os.getenv('FLASK_ENV') != 'production':
            db.create_all()
            
        if Office.query.count() == 0:
            print("Seeding initial offices...")
            offices = [
                {'name': 'Accounts'},
                {'name': 'HR'},
                {'name': 'PMU'},
                {'name': 'Secretaries'},
                {'name': 'ICT'}
            ]
            for o in offices:
                db.session.add(Office(**o))
            db.session.commit()
            
            # Create an admin user automatically for testing
            admin = User(
                email='admin@ticketing.local',
                password_hash=generate_password_hash('password'),
                displayName='System Admin',
                role='ADMIN',
                officeId=Office.query.filter_by(name='ICT').first().id
            )
            db.session.add(admin)
            db.session.commit()
            print("Seeded database successfully.")

if __name__ == '__main__':
    create_db_and_seed()
    app.run(debug=True, port=5000, host='0.0.0.0')
