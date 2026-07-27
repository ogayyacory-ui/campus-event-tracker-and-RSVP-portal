# resources/auth.py
from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from models import db, User, OrganizerProfile

# Custom Role Authorization Decorator
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or user.role != 'admin':
                return {'error': 'Forbidden: Admin access required'}, 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper

class RegisterResource(Resource):
    def post(self):
        data = request.get_json()
        
        if User.query.filter((User.email == data.get('email')) | (User.username == data.get('username'))).first():
            return {'error': 'Username or Email already exists'}, 400

        hashed_pw = generate_password_hash(data['password'])
        
        new_user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hashed_pw,
            role=data.get('role', 'student')
        )
        db.session.add(new_user)
        db.session.commit()

        # If registering as admin/organizer, create Profile automatically
        if new_user.role == 'admin':
            profile = OrganizerProfile(
                user_id=new_user.id,
                organization_name=data.get('organization_name', 'Campus Club'),
                department=data.get('department', 'General')
            )
            db.session.add(profile)
            db.session.commit()

        return {'message': 'User registered successfully'}, 201


class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data.get('email')).first()

        if user and check_password_hash(user.password_hash, data.get('password')):
            access_token = create_access_token(identity=user.id)
            return {
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            }, 200

        return {'error': 'Invalid credentials'}, 401