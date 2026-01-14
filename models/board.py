"""Board model - Represents a surfboard using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db
from utils.constants import (
    BOARD_STATUS_AVAILABLE, BOARD_STATUS_CHECKED_OUT, BOARD_STATUS_DAMAGED,
    BOARD_STATUS_IN_REPAIR, BOARD_STATUS_REPLACED,
    BOARD_CONDITION_EXCELLENT, BOARD_CONDITION_GOOD, BOARD_CONDITION_FAIR
)


class Board(db.Model):
    """Represents a surfboard in the system"""
    __tablename__ = 'boards'
    
    STATUS_AVAILABLE = BOARD_STATUS_AVAILABLE
    STATUS_CHECKED_OUT = BOARD_STATUS_CHECKED_OUT
    STATUS_DAMAGED = BOARD_STATUS_DAMAGED
    STATUS_IN_REPAIR = BOARD_STATUS_IN_REPAIR
    STATUS_REPLACED = BOARD_STATUS_REPLACED
    
    CONDITION_EXCELLENT = BOARD_CONDITION_EXCELLENT
    CONDITION_GOOD = BOARD_CONDITION_GOOD
    CONDITION_FAIR = BOARD_CONDITION_FAIR
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    location_id = db.Column(db.String(36), db.ForeignKey('locations.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    brand = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default=BOARD_STATUS_AVAILABLE, nullable=False)
    condition = db.Column(db.String(50), default=BOARD_CONDITION_GOOD, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, id=None, location_id=None, name=None, brand=None, 
                 size=None, status=None, condition=None, created_at=None, updated_at=None):
        if id:
            self.id = id
        self.location_id = location_id
        self.name = name
        self.brand = brand
        self.size = size
        self.status = status or self.STATUS_AVAILABLE
        self.condition = condition or self.CONDITION_GOOD
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, board_id):
        """Find a board by ID"""
        return cls.query.get(board_id)
    
    @classmethod
    def find_by_location(cls, location_id):
        """Find all boards at a location"""
        return cls.query.filter_by(location_id=location_id).order_by(cls.name).all()
    
    @classmethod
    def find_available(cls, location_id):
        """Find available boards at a location"""
        return cls.query.filter_by(location_id=location_id, status=cls.STATUS_AVAILABLE).order_by(cls.name).all()
    
    @classmethod
    def find_by_status(cls, location_id, status):
        """Find boards by status at a location"""
        return cls.query.filter_by(location_id=location_id, status=status).order_by(cls.name).all()
    
    @classmethod
    def find_all(cls):
        """Find all boards"""
        return cls.query.all()
    
    def update_status(self, new_status):
        """Update board status"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_available(self):
        """Check if board is available for checkout"""
        return self.status == self.STATUS_AVAILABLE
    
    def save(self):
        """Save board to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'location_id': self.location_id,
            'name': self.name,
            'brand': self.brand,
            'size': self.size,
            'status': self.status,
            'condition': self.condition,
            'is_available': self.is_available(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Board {self.name}>'
