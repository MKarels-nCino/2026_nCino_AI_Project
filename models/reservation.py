"""Reservation model - Represents a board reservation using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db
from utils.constants import (
    RESERVATION_STATUS_PENDING, RESERVATION_STATUS_AVAILABLE,
    RESERVATION_STATUS_FULFILLED, RESERVATION_STATUS_CANCELLED
)


class Reservation(db.Model):
    """Represents a reservation for a board"""
    __tablename__ = 'reservations'
    
    STATUS_PENDING = RESERVATION_STATUS_PENDING
    STATUS_AVAILABLE = RESERVATION_STATUS_AVAILABLE
    STATUS_FULFILLED = RESERVATION_STATUS_FULFILLED
    STATUS_CANCELLED = RESERVATION_STATUS_CANCELLED
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    board_id = db.Column(db.String(36), db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False)
    checkout_id = db.Column(db.String(36), db.ForeignKey('checkouts.id', ondelete='CASCADE'), nullable=True)
    reservation_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    unlock_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default=RESERVATION_STATUS_PENDING, nullable=False)
    notification_sent = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, id=None, user_id=None, board_id=None, checkout_id=None,
                 reservation_time=None, unlock_time=None, status=None,
                 notification_sent=None, created_at=None, updated_at=None):
        if id:
            self.id = id
        self.user_id = user_id
        self.board_id = board_id
        self.checkout_id = checkout_id
        self.reservation_time = reservation_time or datetime.utcnow()
        self.unlock_time = unlock_time
        self.status = status or self.STATUS_PENDING
        self.notification_sent = notification_sent or False
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, reservation_id):
        """Find a reservation by ID"""
        return cls.query.get(reservation_id)
    
    @classmethod
    def find_by_user(cls, user_id):
        """Find all reservations for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.unlock_time.asc()).all()
    
    @classmethod
    def find_pending_by_board(cls, board_id):
        """Find pending reservations for a board (queue)"""
        return cls.query.filter_by(board_id=board_id, status=cls.STATUS_PENDING).order_by(cls.unlock_time.asc(), cls.reservation_time.asc()).all()
    
    @classmethod
    def find_available(cls, board_id):
        """Find available reservations (unlock time has passed)"""
        return cls.query.filter_by(board_id=board_id, status=cls.STATUS_PENDING).filter(cls.unlock_time <= datetime.utcnow()).order_by(cls.unlock_time.asc(), cls.reservation_time.asc()).first()
    
    @classmethod
    def find_pending_notifications(cls):
        """Find reservations that need notifications sent"""
        return cls.query.filter_by(status=cls.STATUS_PENDING, notification_sent=False).filter(cls.unlock_time <= datetime.utcnow()).order_by(cls.unlock_time.asc()).all()
    
    def save(self):
        """Save reservation to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def mark_available(self):
        """Mark reservation as available (unlock time has passed)"""
        self.status = self.STATUS_AVAILABLE
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_fulfilled(self):
        """Mark reservation as fulfilled"""
        self.status = self.STATUS_FULFILLED
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def mark_notification_sent(self):
        """Mark notification as sent"""
        self.notification_sent = True
        db.session.commit()
    
    def cancel(self):
        """Cancel a reservation"""
        self.status = self.STATUS_CANCELLED
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_pending(self):
        """Check if reservation is pending"""
        return self.status == self.STATUS_PENDING
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'board_id': self.board_id,
            'checkout_id': self.checkout_id,
            'reservation_time': self.reservation_time.isoformat() if self.reservation_time else None,
            'unlock_time': self.unlock_time.isoformat() if self.unlock_time else None,
            'status': self.status,
            'notification_sent': self.notification_sent,
            'is_pending': self.is_pending(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Reservation {self.id}>'
