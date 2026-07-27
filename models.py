# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime

db = SQLAlchemy()

# -------------------------------------------------------------------
# 1. USER MODEL
# -------------------------------------------------------------------
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student') # 'student' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 1:1 Relationship (User -> Profile)
    organizer_profile = db.relationship(
        'OrganizerProfile', 
        back_populates='user', 
        uselist=False, 
        cascade='all, delete-orphan'
    )
    
    # 1:M Relationship with RSVP
    rsvps = db.relationship('RSVP', back_populates='user', cascade='all, delete-orphan')

    # Prevent infinite recursion loops in serialization
    serialize_rules = ('-password_hash', '-organizer_profile.user', '-rsvps.user')


# -------------------------------------------------------------------
# 2. ORGANIZER PROFILE (1:1 with User)
# -------------------------------------------------------------------
class OrganizerProfile(db.Model, SerializerMixin):
    __tablename__ = 'organizer_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    organization_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False) # Academic, Sports, Cultural, etc.
    is_verified = db.Column(db.Boolean, default=True)

    user = db.relationship('User', back_populates='organizer_profile')
    events = db.relationship('Event', back_populates='organizer', cascade='all, delete-orphan')

    serialize_rules = ('-user.organizer_profile', '-events.organizer')


# -------------------------------------------------------------------
# 3. EVENT MODEL (1:N with OrganizerProfile)
# -------------------------------------------------------------------
class Event(db.Model, SerializerMixin):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False) # academic, social, sports
    location = db.Column(db.String(150), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey('organizer_profiles.id'), nullable=False)

    organizer = db.relationship('OrganizerProfile', back_populates='events')
    rsvps = db.relationship('RSVP', back_populates='event', cascade='all, delete-orphan')

    serialize_rules = ('-organizer.events', '-rsvps.event')


# -------------------------------------------------------------------
# 4. RSVP MODEL (M:N Association Model)
# -------------------------------------------------------------------
class RSVP(db.Model, SerializerMixin):
    __tablename__ = 'rsvps'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    
    # Extra Association Attributes (Deep M:N concept)
    ticket_type = db.Column(db.String(30), default='General') # General, VIP, Student
    status = db.Column(db.String(20), default='attending')    # attending, waitlisted, cancelled
    checked_in = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='rsvps')
    event = db.relationship('Event', back_populates='rsvps')

    serialize_rules = ('-user.rsvps', '-event.rsvps')