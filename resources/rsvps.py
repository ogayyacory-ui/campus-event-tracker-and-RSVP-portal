
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, RSVP, Event

class RSVPResource(Resource):
    @jwt_required()
    def post(self, event_id):
        current_user_id = int(get_jwt_identity())
        event = Event.query.get_or_404(event_id)
        
        # Check existing RSVP
        existing_rsvp = RSVP.query.filter_by(user_id=current_user_id, event_id=event_id).first()
        if existing_rsvp:
            return {'error': 'You have already RSVPed for this event'}, 400

        if RSVP.query.filter_by(event_id=event_id, status='attending').count() >= event.capacity:
            return {'error': 'This event is at capacity'}, 409

        data = request.get_json(silent=True) or {}
        new_rsvp = RSVP(
            user_id=current_user_id,
            event_id=event_id,
            ticket_type=data.get('ticket_type', 'General'),
            status='attending'
        )
        db.session.add(new_rsvp)
        db.session.commit()
        return new_rsvp.to_dict(), 201


class UserRSVPListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = int(get_jwt_identity())
        rsvps = RSVP.query.filter_by(user_id=current_user_id).all()
        return [rsvp.to_dict() for rsvp in rsvps], 200
