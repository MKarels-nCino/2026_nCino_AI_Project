"""Auth service - Handles user authentication using SQLAlchemy"""
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User
from utils.constants import (
    ERROR_USER_NOT_FOUND, ERROR_INVALID_CREDENTIALS,
    USER_ROLE_USER
)
import logging
import uuid

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication using SQLAlchemy"""
    
    def __init__(self):
        # No Supabase initialization needed
        logger.info("AuthService initialized (SQLAlchemy)")
    
    def sign_up(self, email, password, full_name, location_id, role=None):
        """Register a new user"""
        if role is None:
            role = USER_ROLE_USER
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            raise Exception("User with this email already exists")
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Create user in database
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=full_name,
            location_id=location_id,
            role=role
        )
        # Store password hash (we'll need to add this field to User model)
        user.password_hash = password_hash
        user.save()
        
        logger.info(f"User registered: {email}")
        return user
    
    def sign_in(self, email, password):
        """Sign in a user"""
        user = User.find_by_email(email)
        if not user:
            raise Exception(ERROR_USER_NOT_FOUND)
        
        # Check password
        if not hasattr(user, 'password_hash') or not check_password_hash(user.password_hash, password):
            raise Exception(ERROR_INVALID_CREDENTIALS)
        
        logger.info(f"User signed in: {email}")
        return user, None  # No session data needed with Flask-Login
    
    def sign_out(self, access_token=None):
        """Sign out a user"""
        # Flask-Login handles this automatically
        logger.info("User signed out")
    
    def get_user_from_token(self, access_token):
        """Get user from access token (not used with Flask-Login)"""
        return None
    
    def verify_user(self, user_id):
        """Verify user exists and return user object"""
        return User.find_by_id(user_id)
