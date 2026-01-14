"""Location model - Represents a physical location using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db


class Location(db.Model):
    """Represents a physical location"""
    __tablename__ = 'locations'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    timezone = db.Column(db.String(100), default='America/Los_Angeles', nullable=False)
    address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @classmethod
    def find_all(cls):
        """Find all locations"""
        return cls.query.all()
    
    @classmethod
    def find_by_id(cls, location_id):
        """Find a location by ID"""
        return cls.query.get(location_id)
    
    def save(self):
        """Save location to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def __repr__(self):
        return f'<Location {self.name}>'
