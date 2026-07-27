# seed.py
from app import app
from models import db, User, OrganizerProfile, Event, RSVP
from werkzeug.security import generate_password_hash
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

with app.app_context():
    print("Clearing old data...")
    RSVP.query.delete()
    Event.query.delete()
    OrganizerProfile.query.delete()
    User.query.delete()

    print("Seeding Users and Profiles...")
    # Admin User
    admin = User(
        username="admin_dept",
        email="admin@campus.edu",
        password_hash=generate_password_hash("admin123"),
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()

    admin_profile = OrganizerProfile(
        user_id=admin.id,
        organization_name="Student Affairs",
        department="Academic"
    )
    db.session.add(admin_profile)

    # Regular Students
    students = []
    for _ in range(10):
        student = User(
            username=fake.user_name(),
            email=fake.email(),
            password_hash=generate_password_hash("password123"),
            role="student"
        )
        students.append(student)
        db.session.add(student)
    
    db.session.commit()

    print("Seeding Events...")
    categories = ['academic', 'social', 'sports']
    events = []
    for _ in range(8):
        event = Event(
            title=fake.catch_phrase(),
            description=fake.paragraph(),
            category=random.choice(categories),
            location=f"Hall {random.randint(1, 10)}",
            capacity=random.randint(30, 200),
            event_date=datetime.now() + timedelta(days=random.randint(1, 30)),
            organizer_id=admin_profile.id
        )
        events.append(event)
        db.session.add(event)

    db.session.commit()

    print("Seeding RSVPs (Many:Many with extra data)...")
    ticket_types = ['General', 'VIP', 'Student']
    for student in students:
        # Assign 1 to 3 random event RSVPs per student
        for event in random.sample(events, k=random.randint(1, 3)):
            rsvp = RSVP(
                user_id=student.id,
                event_id=event.id,
                ticket_type=random.choice(ticket_types),
                status='attending',
                checked_in=random.choice([True, False])
            )
            db.session.add(rsvp)

    db.session.commit()
    print("Database seeded successfully!")