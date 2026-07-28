# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base Configuration Options"""
    
    # Flask Secret Key
    SECRET_KEY = os.getenv(
        'SECRET_KEY', 'development-only-secret-key-change-this-before-deployment'
    )
    
    # SQLAlchemy Database Setup.  A local SQLite database makes the project
    # runnable out of the box; deployments can provide DATABASE_URL or the
    # legacy DATABASE_URI value for PostgreSQL.
    SQLALCHEMY_DATABASE_URI = (
        os.getenv('DATABASE_URL')
        or os.getenv('DATABASE_URI')
        or f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'campus_events.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-JWT-Extended Setup
    JWT_SECRET_KEY = os.getenv(
        'JWT_SECRET', 'development-only-jwt-secret-change-this-before-deployment'
    )
    
    # Optional: Set JWT Expiration (e.g., 2 hours)
    # from datetime import timedelta
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)


class DevelopmentConfig(Config):
    """Development Environment Specific Config"""
    DEBUG = True


class ProductionConfig(Config):
    """Production Environment Specific Config"""
    DEBUG = False


class TestingConfig(Config):
    """Isolated configuration used by the automated test suite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


# Dictionary mapping names to configuration classes
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
