# seed.py
from app import create_app
from models import db, User, OrganizerProfile, Event, RSVP
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = create_app('development')

with app.app_context():
    print("Clearing existing data...")
    RSVP.query.delete()
    Event.query.delete()
    OrganizerProfile.query.delete()
    User.query.delete()

    print("Seeding Users...")
    # Admin / Organizer User
    admin_user = User(
        username="admin_kagwiria",
        email="kagwiria@campus.edu",
        password_hash=generate_password_hash("kag123"),
        role="admin"
    )

    # Standard Student Users
    students = [
        User(
            username="Omondi_c",
            email="omosh@campus.edu",
            password_hash=generate_password_hash("omosH123"),
            role="student"
        ),
        User(
            username="Matiku_m",
            email="matiku@campus.edu",
            password_hash=generate_password_hash("pMNm123"),
            role="student"
        ),
        User(
            username="maya_p",
            email="maya@campus.edu",
            password_hash=generate_password_hash("@maya123"),
            role="student"
        ),
        User(
            username="Wafula_k",
            email="Wafula@campus.edu",
            password_hash=generate_password_hash("3fuls"),
            role="student"
        )
    ]

    db.session.add(admin_user)
    db.session.add_all(students)
    db.session.commit()

    print("Seeding Organizer Profile...")
    organizer = OrganizerProfile(
        user_id=admin_user.id,
        organization_name="Campus Activity Board",
        department="Student Life",
        is_verified=True
    )
    db.session.add(organizer)
    db.session.commit()

    print("Seeding Events...")
    now = datetime.now()
    mock_events = [
        Event(
            title="Annual Tech Symposium 2026",
            description="Explore innovations in AI, software engineering, and robotics with industry guest speakers.",
            category="academic",
            location="Engineering Hall 101",
            capacity=150,
            event_date=now + timedelta(days=3),
            organizer_id=organizer.id
        ),
        Event(
            title="Campus Welcome Night & Concert",
            description="Live music, free food trucks, and games for all new and returning students.",
            category="social",
            location="Student Center Plaza",
            capacity=300,
            event_date=now + timedelta(days=7),
            organizer_id=organizer.id
        ),
        Event(
            title="Inter-Department Basketball Finals",
            description="Watch Computer Science face off against Business Administration in the championship game.",
            category="sports",
            location="Campus Recreation Gym",
            capacity=200,
            event_date=now + timedelta(days=12),
            organizer_id=organizer.id
        ),
        Event(
            title="AI & Web Dev Workshop",
            description="Hands-on coding session covering React and Python backend architectures.",
            category="academic",
            location="Science Complex Lab 3B",
            capacity=40,
            event_date=now + timedelta(days=18),
            organizer_id=organizer.id
        ),
        Event(
            title="Outdoor Cinema: Movie Under the Stars",
            description="Bring your blankets and snacks for a screening on the main quad lawn.",
            category="social",
            location="Student center",
            capacity=250,
            event_date=now + timedelta(days=22),
            organizer_id=organizer.id
        )
    ]

    db.session.add_all(mock_events)
    db.session.commit()

    print("Seeding RSVPs (M:N Association Attributes)...")
    # Mapping specific RSVPs so you have predictable test data
    mock_rsvps = [
        # Event 1: Tech Symposium
        RSVP(user_id=students[0].id, event_id=mock_events[0].id, ticket_type="General", status="attending", checked_in=True),
        RSVP(user_id=students[1].id, event_id=mock_events[0].id, ticket_type="VIP", status="attending", checked_in=False),
        RSVP(user_id=students[2].id, event_id=mock_events[0].id, ticket_type="Student", status="attending", checked_in=True),
        
        # Event 2: Welcome Night
        RSVP(user_id=students[0].id, event_id=mock_events[1].id, ticket_type="General", status="attending", checked_in=False),
        RSVP(user_id=students[3].id, event_id=mock_events[1].id, ticket_type="General", status="attending", checked_in=False),
        
        # Event 3: Basketball Finals
        RSVP(user_id=students[1].id, event_id=mock_events[2].id, ticket_type="Student", status="attending", checked_in=True),
        RSVP(user_id=students[2].id, event_id=mock_events[2].id, ticket_type="Student", status="cancelled", checked_in=False),

        # Event 4: AI Workshop
        RSVP(user_id=students[0].id, event_id=mock_events[3].id, ticket_type="VIP", status="attending", checked_in=False),
    ]

    db.session.add_all(mock_rsvps)
    db.session.commit()

    print("Database successfully seeded with mock data!")