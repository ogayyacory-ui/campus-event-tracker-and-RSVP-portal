
import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from dotenv import load_dotenv

from models import db
from resources.auth import RegisterResource, LoginResource
from resources.events import EventListResource, EventDetailResource
from resources.rsvps import RSVPResource, UserRSVPListResource
from resources.analytics import AnalyticsResource

load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'postgresql://localhost/campusevents_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret-key-change-me')

# Initialize Extensions
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)
api = Api(app)

# Register Routes
api.add_resource(RegisterResource, '/api/auth/register')
api.add_resource(LoginResource, '/api/auth/login')
api.add_resource(EventListResource, '/api/events')
api.add_resource(EventDetailResource, '/api/events/<int:event_id>')
api.add_resource(RSVPResource, '/api/events/<int:event_id>/rsvp')
api.add_resource(UserRSVPListResource, '/api/users/me/rsvps')
api.add_resource(AnalyticsResource, '/api/analytics/summary')

if __name__ == '__main__':
    app.run(port=5000, debug=True)