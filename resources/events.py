
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Event, User, OrganizerProfile
from resources.auth import admin_required


EVENT_FIELDS = {'title', 'description', 'category', 'location', 'capacity', 'event_date'}


def event_payload(data, partial=False):
    if not isinstance(data, dict):
        return None, 'A JSON object is required'
    if not partial:
        missing = EVENT_FIELDS - data.keys()
        if missing:
            return None, f"Missing required field(s): {', '.join(sorted(missing))}"

    payload = {key: value for key, value in data.items() if key in EVENT_FIELDS}
    if 'capacity' in payload:
        try:
            payload['capacity'] = int(payload['capacity'])
        except (TypeError, ValueError):
            return None, 'Capacity must be a whole number'
        if payload['capacity'] < 1:
            return None, 'Capacity must be at least 1'
    if 'event_date' in payload:
        try:
            payload['event_date'] = datetime.fromisoformat(payload['event_date'])
        except (TypeError, ValueError):
            return None, 'event_date must be a valid ISO-8601 datetime'
    for field in ('title', 'description', 'category', 'location'):
        if field in payload and not str(payload[field]).strip():
            return None, f'{field} cannot be empty'
    return payload, None

class EventListResource(Resource):
    def get(self):
        # 1. Mandatory Pagination via Query Params
        page = max(request.args.get('page', 1, type=int) or 1, 1)
        per_page = min(max(request.args.get('per_page', 6, type=int) or 6, 1), 100)
        
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
        user = db.session.get(User, int(current_user_id))
        
        if not user.organizer_profile:
            return {'error': 'User lacks an organizer profile'}, 400

        data, error = event_payload(request.get_json(silent=True))
        if error:
            return {'error': error}, 400
        new_event = Event(
            **data,
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
        if event.organizer.user_id != int(get_jwt_identity()):
            return {'error': 'You can only modify your own events'}, 403
        data, error = event_payload(request.get_json(silent=True), partial=True)
        if error:
            return {'error': error}, 400

        for key, value in data.items():
            if key in EVENT_FIELDS:
                setattr(event, key, value)

        db.session.commit()
        return event.to_dict(), 200

    @admin_required()
    def delete(self, event_id):
        event = Event.query.get_or_404(event_id)
        if event.organizer.user_id != int(get_jwt_identity()):
            return {'error': 'You can only delete your own events'}, 403
        db.session.delete(event)
        db.session.commit()
        return {'message': 'Event deleted successfully'}, 200
