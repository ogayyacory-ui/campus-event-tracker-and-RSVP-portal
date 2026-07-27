
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Event, User, OrganizerProfile
from resources.auth import admin_required

class EventListResource(Resource):
    def get(self):
        # 1. Mandatory Pagination via Query Params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 6, type=int)
        
        # Filtering parameters
        category = request.args.get('category')
        search = request.args.get('search')

        query = Event.query

        if category:
            query = query.filter(Event.category == category)
        if search:
            query = query.filter(Event.title.ilike(f'%{search}%'))

        # SQLAlchemy Paginate
        paginated_events = query.order_by(Event.event_date.asc()).paginate(page=page, per_page=per_page, error_out=False)

        return {
            'total': paginated_events.total,
            'page': paginated_events.page,
            'per_page': paginated_events.per_page,
            'total_pages': paginated_events.pages,
            'items': [event.to_dict() for event in paginated_events.items]
        }, 200

    @admin_required()
    def post(self):
        # Admin / Organizer restricted endpoint
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user.organizer_profile:
            return {'error': 'User lacks an organizer profile'}, 400

        data = request.get_json()
        new_event = Event(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            location=data['location'],
            capacity=data['capacity'],
            event_date=datetime.fromisoformat(data['event_date']),
            organizer_id=user.organizer_profile.id
        )
        db.session.add(new_event)
        db.session.commit()
        return new_event.to_dict(), 201


class EventDetailResource(Resource):
    def get(self, event_id):
        event = Event.query.get_or_404(event_id)
        return event.to_dict(), 200

    @admin_required()
    def patch(self, event_id):
        event = Event.query.get_or_404(event_id)
        data = request.get_json()

        for key, value in data.items():
            if key == 'event_date':
                setattr(event, key, datetime.fromisoformat(value))
            elif hasattr(event, key):
                setattr(event, key, value)

        db.session.commit()
        return event.to_dict(), 200

    @admin_required()
    def delete(self, event_id):
        event = Event.query.get_or_404(event_id)
        db.session.delete(event)
        db.session.commit()
        return {'message': 'Event deleted successfully'}, 200