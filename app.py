# app.py
import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

from models import db
from config import config
from controllers.auth import RegisterResource, LoginResource
from controllers.events import EventListResource, EventDetailResource
from controllers.rsvps import RSVPResource, UserRSVPListResource
from controllers.analytics import AnalyticsResource

load_dotenv()

# Initialize extensions globally without binding to an app yet
migrate = Migrate()
jwt = JWTManager()
cors = CORS()

def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    # 1. Create app instance
    app = Flask(__name__)

    # 2. Load settings from config.py based on environment
    app.config.from_object(config[config_name])

    # 3. Bind extensions to app instance
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    # 4. Register API endpoints
    api = Api(app)
    api.add_resource(RegisterResource, '/api/auth/register')
    api.add_resource(LoginResource, '/api/auth/login')
    api.add_resource(EventListResource, '/api/events')
    api.add_resource(EventDetailResource, '/api/events/<int:event_id>')
    api.add_resource(RSVPResource, '/api/events/<int:event_id>/rsvp')
    api.add_resource(UserRSVPListResource, '/api/users/me/rsvps')
    api.add_resource(AnalyticsResource, '/api/analytics/summary')

    return app

# Instantiate app for running directly or via WSGI/Flask CLI
app = create_app()

if __name__ == '__main__':
    app.run(port=5000, debug=True)