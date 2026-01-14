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
    image_url = db.Column(db.String(500), nullable=True)  # URL to surfboard image
    status = db.Column(db.String(50), default=BOARD_STATUS_AVAILABLE, nullable=False)
    condition = db.Column(db.String(50), default=BOARD_CONDITION_GOOD, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, id=None, location_id=None, name=None, brand=None, 
                 size=None, image_url=None, status=None, condition=None, created_at=None, updated_at=None):
        if id:
            self.id = id
        self.location_id = location_id
        self.name = name
        self.brand = brand
        self.size = size
        self.image_url = image_url
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
    
    def is_available_at_datetime(self, checkout_datetime, duration_hours=1):
        """
        Check if board is available at a specific datetime for the given duration
        Checks both active/scheduled checkouts and reservations for time overlap
        Returns: (is_available, reason)
        """
        from models.checkout import Checkout
        from models.reservation import Reservation
        from datetime import timedelta
        
        # Convert checkout_datetime to naive UTC for comparison (strip timezone info)
        if checkout_datetime.tzinfo is not None:
            checkout_start = checkout_datetime.replace(tzinfo=None)
        else:
            checkout_start = checkout_datetime
        
        checkout_end = checkout_start + timedelta(hours=duration_hours)
        
        # Check for active checkouts that overlap (STATUS_ACTIVE includes both scheduled and in-use)
        active_checkouts = Checkout.query.filter_by(
            board_id=self.id,
            status=Checkout.STATUS_ACTIVE
        ).all()
        
        for checkout in active_checkouts:
            # Get checkout time range (database times are naive UTC)
            existing_start = checkout.checkout_time
            existing_end = checkout.expected_return_time or (existing_start + timedelta(hours=1))
            
            # Check for time overlap: new checkout overlaps if it starts before existing ends AND ends after existing starts
            if checkout_start < existing_end and checkout_end > existing_start:
                return False, "Reserved"
        
        # Check for pending/available reservations that overlap (by date for now)
        reservations = Reservation.query.filter_by(
            board_id=self.id
        ).filter(
            Reservation.status.in_([Reservation.STATUS_PENDING, Reservation.STATUS_AVAILABLE])
        ).all()
        
        for reservation in reservations:
            reservation_date = reservation.unlock_time.date()
            # Only mark as reserved if dates overlap
            if checkout_start.date() == reservation_date:
                return False, "Reserved"
        
        return True, None
    
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
            'image_url': self.image_url,
            'status': self.status,
            'condition': self.condition,
            'is_available': self.is_available(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Board {self.name}>'
