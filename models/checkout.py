"""Checkout model - Represents a board checkout transaction using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db
from utils.constants import (
    CHECKOUT_STATUS_ACTIVE, CHECKOUT_STATUS_RETURNED, CHECKOUT_STATUS_CANCELLED
)


class Checkout(db.Model):
    """Represents a checkout transaction"""
    __tablename__ = 'checkouts'
    
    STATUS_ACTIVE = CHECKOUT_STATUS_ACTIVE
    STATUS_RETURNED = CHECKOUT_STATUS_RETURNED
    STATUS_CANCELLED = CHECKOUT_STATUS_CANCELLED
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    board_id = db.Column(db.String(36), db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False)
    checkout_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expected_return_time = db.Column(db.DateTime, nullable=False)
    actual_return_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default=CHECKOUT_STATUS_ACTIVE, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, id=None, user_id=None, board_id=None, checkout_time=None,
                 expected_return_time=None, actual_return_time=None, status=None,
                 created_at=None, updated_at=None):
        if id:
            self.id = id
        self.user_id = user_id
        self.board_id = board_id
        self.checkout_time = checkout_time or datetime.utcnow()
        self.expected_return_time = expected_return_time
        self.actual_return_time = actual_return_time
        self.status = status or self.STATUS_ACTIVE
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, checkout_id):
        """Find a checkout by ID"""
        return cls.query.get(checkout_id)
    
    @classmethod
    def find_active_by_user(cls, user_id):
        """Find active checkouts for a user"""
        return cls.query.filter_by(user_id=user_id, status=cls.STATUS_ACTIVE).order_by(cls.checkout_time.desc()).all()
    
    @classmethod
    def find_by_user(cls, user_id, limit=None):
        """Find all checkouts for a user"""
        query = cls.query.filter_by(user_id=user_id).order_by(cls.checkout_time.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def find_active_by_board(cls, board_id):
        """Find active checkout for a board"""
        return cls.query.filter_by(board_id=board_id, status=cls.STATUS_ACTIVE).order_by(cls.checkout_time.desc()).first()
    
    @classmethod
    def find_by_location(cls, location_id, limit=None):
        """Find all checkouts at a location"""
        from models.board import Board
        query = cls.query.join(Board).filter(Board.location_id == location_id).order_by(cls.checkout_time.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    def save(self):
        """Save checkout to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def mark_returned(self, return_time=None):
        """Mark checkout as returned"""
        if return_time is None:
            return_time = datetime.utcnow()
        self.status = self.STATUS_RETURNED
        self.actual_return_time = return_time
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def cancel(self):
        """Cancel a checkout"""
        self.status = self.STATUS_CANCELLED
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def is_active(self):
        """Check if checkout is active"""
        return self.status == self.STATUS_ACTIVE
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'board_id': self.board_id,
            'checkout_time': self.checkout_time.isoformat() if self.checkout_time else None,
            'expected_return_time': self.expected_return_time.isoformat() if self.expected_return_time else None,
            'actual_return_time': self.actual_return_time.isoformat() if self.actual_return_time else None,
            'status': self.status,
            'is_active': self.is_active(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Checkout {self.id}>'
