"""User model - Represents a system user using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    """Represents a user in the system (using SQLAlchemy)"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Password hash for authentication
    location_id = db.Column(db.String(36), db.ForeignKey('locations.id', ondelete='SET NULL'), nullable=True)
    role = db.Column(db.String(50), default='user', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, id=None, email=None, full_name=None, location_id=None,
                 role='user', password_hash=None, created_at=None, updated_at=None):
        if id:
            self.id = id
        self.email = email
        self.full_name = full_name
        self.password_hash = password_hash
        self.location_id = location_id
        self.role = role
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, user_id):
        """Find a user by ID"""
        return cls.query.get(user_id)
    
    @classmethod
    def find_by_email(cls, email):
        """Find a user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_location(cls, location_id):
        """Find all users at a location"""
        return cls.query.filter_by(location_id=location_id).all()
    
    def save(self):
        """Save user to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def update(self, **kwargs):
        """Update user attributes"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
    
    def delete(self):
        """Delete user from database"""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary (excludes password_hash for security)"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'location_id': self.location_id,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_admin(self):
        """Check if user is an admin"""
        from utils.constants import USER_ROLE_ADMIN
        return self.role == USER_ROLE_ADMIN
    
    def __repr__(self):
        return f'<User {self.email}>'
