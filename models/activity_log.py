"""Activity log model - Represents system activity using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db
import json
from utils.constants import (
    ACTION_CHECKOUT, ACTION_RETURN, ACTION_RESERVATION, ACTION_DAMAGE_REPORT,
    ACTION_CANCEL_CHECKOUT, ACTION_CANCEL_RESERVATION,
    ACTION_BOARD_STATUS_CHANGE, ACTION_DAMAGE_STATUS_CHANGE
)


class ActivityLog(db.Model):
    """Represents an activity log entry"""
    __tablename__ = 'activity_log'
    
    ACTION_CHECKOUT = ACTION_CHECKOUT
    ACTION_RETURN = ACTION_RETURN
    ACTION_RESERVATION = ACTION_RESERVATION
    ACTION_DAMAGE_REPORT = ACTION_DAMAGE_REPORT
    ACTION_CANCEL_CHECKOUT = ACTION_CANCEL_CHECKOUT
    ACTION_CANCEL_RESERVATION = ACTION_CANCEL_RESERVATION
    ACTION_BOARD_STATUS_CHANGE = ACTION_BOARD_STATUS_CHANGE
    ACTION_DAMAGE_STATUS_CHANGE = ACTION_DAMAGE_STATUS_CHANGE
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    board_id = db.Column(db.String(36), db.ForeignKey('boards.id', ondelete='SET NULL'), nullable=True)
    action_type = db.Column(db.String(50), nullable=False)
    action_details = db.Column(db.Text, nullable=True)  # JSON stored as text
    location_id = db.Column(db.String(36), db.ForeignKey('locations.id', ondelete='SET NULL'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    
    def __init__(self, id=None, user_id=None, board_id=None, action_type=None,
                 action_details=None, location_id=None, timestamp=None, ip_address=None):
        if id:
            self.id = id
        self.user_id = user_id
        self.board_id = board_id
        self.action_type = action_type
        # Store action_details as JSON string
        if action_details:
            if isinstance(action_details, dict):
                self.action_details = json.dumps(action_details)
            else:
                self.action_details = action_details
        else:
            self.action_details = None
        self.location_id = location_id
        self.timestamp = timestamp or datetime.utcnow()
        self.ip_address = ip_address
    
    @property
    def action_details_dict(self):
        """Get action_details as a dictionary"""
        if self.action_details:
            try:
                return json.loads(self.action_details)
            except:
                return {}
        return {}
    
    @classmethod
    def find_by_id(cls, log_id):
        """Find an activity log by ID"""
        return cls.query.get(log_id)
    
    @classmethod
    def find_by_location(cls, location_id, limit=100):
        """Find activity logs for a location"""
        return cls.query.filter_by(location_id=location_id).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def find_by_user(cls, user_id, limit=50):
        """Find activity logs for a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def find_by_board(cls, board_id, limit=50):
        """Find activity logs for a board"""
        return cls.query.filter_by(board_id=board_id).order_by(cls.timestamp.desc()).limit(limit).all()
    
    def save(self):
        """Save activity log to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    @classmethod
    def create_log(cls, user_id, board_id, action_type, action_details, location_id, ip_address=None):
        """Create and save an activity log entry"""
        log = cls(
            user_id=user_id,
            board_id=board_id,
            action_type=action_type,
            action_details=action_details,
            location_id=location_id,
            ip_address=ip_address
        )
        log.save()
        return log
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'board_id': self.board_id,
            'action_type': self.action_type,
            'action_details': self.action_details_dict,
            'location_id': self.location_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address
        }
    
    def __repr__(self):
        return f'<ActivityLog {self.action_type} at {self.timestamp}>'