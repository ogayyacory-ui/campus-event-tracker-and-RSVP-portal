
from flask_restful import Resource
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from models import db, Event, RSVP, OrganizerProfile, User
from resources.auth import admin_required

class AnalyticsResource(Resource):
    @admin_required()
    def get(self):
        
        # QUERY 1: Join + Aggregation + Group By + Having
        # Calculates total RSVPs and events for each department
        
        dept_stats = db.session.query(
            OrganizerProfile.department,
            func.count(RSVP.id).label('total_rsvps'),
            func.count(func.distinct(Event.id)).label('total_events')
        ).join(Event, OrganizerProfile.id == Event.organizer_id)\
         .join(RSVP, Event.id == RSVP.event_id)\
         .group_by(OrganizerProfile.department)\
         .having(func.count(RSVP.id) > 0)\
         .all()

        formatted_stats = [
            {'department': dept, 'total_rsvps': rsvps, 'total_events': events}
            for dept, rsvps, events in dept_stats
        ]

        # QUERY 2: Filter across relationships using .any() & joinedload
        # Gets verified organizer events that currently have active RSVPs
        active_events = Event.query.join(OrganizerProfile)\
            .filter(OrganizerProfile.is_verified == True)\
            .filter(Event.rsvps.any(RSVP.status == 'attending'))\
            .all()

  
        # QUERY 3: Eager Loading (selectinload) to solve N+1 Problem
        # Fetches users who have more than 1 active RSVP along with RSVP data
        
        engaged_users = User.query.options(selectinload(User.rsvps))\
            .join(RSVP)\
            .group_by(User.id)\
            .having(func.count(RSVP.id) >= 1)\
            .all()

        return {
            'department_engagement': formatted_stats,
            'active_verified_events_count': len(active_events),
            'highly_engaged_users_count': len(engaged_users)
        }, 200