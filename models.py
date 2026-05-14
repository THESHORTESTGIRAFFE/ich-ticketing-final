from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
import uuid

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class Office(db.Model):
    __tablename__ = 'offices'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    
    users = db.relationship('User', back_populates='office')
    tickets = db.relationship('Ticket', back_populates='office')

    def __repr__(self):
        return f'<Office {self.name}>'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)  # Changed 'uid' to 'id' for Flask-Login compatibility
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    displayName = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='STAFF') # ADMIN, ICT_OFFICER, TECHNICIAN, INTERN, STAFF
    officeId = db.Column(db.String(36), db.ForeignKey('offices.id'), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_suspended = db.Column(db.Boolean, nullable=False, default=False)

    office = db.relationship('Office', back_populates='users')

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.String(50), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    officeId = db.Column(db.String(36), db.ForeignKey('offices.id'), nullable=False)
    createdBy = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    assignedTo = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True)
    status = db.Column(db.String(50), nullable=False, default='OPEN') # OPEN, IN_PROGRESS, PENDING, RESOLVED, CLOSED
    priority = db.Column(db.String(50), nullable=False, default='MEDIUM') # LOW, MEDIUM, HIGH
    createdAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    respondedAt = db.Column(db.DateTime, nullable=True)
    resolvedAt = db.Column(db.DateTime, nullable=True)

    office = db.relationship('Office', back_populates='tickets')
    creator = db.relationship('User', foreign_keys=[createdBy], backref='created_tickets')
    assignee = db.relationship('User', foreign_keys=[assignedTo], backref='assigned_tickets')
    comments = db.relationship('Comment', back_populates='ticket', cascade="all, delete-orphan")
    activities = db.relationship('ActivityLog', back_populates='ticket', cascade="all, delete-orphan", order_by="desc(ActivityLog.createdAt)")

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    ticketId = db.Column(db.String(36), db.ForeignKey('tickets.id'), nullable=False)
    authorId = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    ticket = db.relationship('Ticket', back_populates='comments')
    author = db.relationship('User', foreign_keys=[authorId])

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    ticketId = db.Column(db.String(36), db.ForeignKey('tickets.id'), nullable=False)
    userId = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    details = db.Column(db.Text, nullable=True)
    createdAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    ticket = db.relationship('Ticket', back_populates='activities')
    user = db.relationship('User', foreign_keys=[userId])
