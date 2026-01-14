"""Activity log model - Represents system activity"""
import uuid
from datetime import datetime
from database import db
import json
from utils.constants import (
    ACTION_CHECKOUT, ACTION_RETURN, ACTION_RESERVATION, ACTION_DAMAGE_REPORT,
    ACTION_CANCEL_CHECKOUT, ACTION_CANCEL_RESERVATION,
    ACTION_BOARD_STATUS_CHANGE, ACTION_DAMAGE_STATUS_CHANGE
)


class ActivityLog:
    """Represents an activity log entry"""
    
    ACTION_CHECKOUT = ACTION_CHECKOUT
    ACTION_RETURN = ACTION_RETURN
    ACTION_RESERVATION = ACTION_RESERVATION
    ACTION_DAMAGE_REPORT = ACTION_DAMAGE_REPORT
    ACTION_CANCEL_CHECKOUT = ACTION_CANCEL_CHECKOUT
    ACTION_CANCEL_RESERVATION = ACTION_CANCEL_RESERVATION
    ACTION_BOARD_STATUS_CHANGE = ACTION_BOARD_STATUS_CHANGE
    ACTION_DAMAGE_STATUS_CHANGE = ACTION_DAMAGE_STATUS_CHANGE
    
    def __init__(self, id=None, user_id=None, board_id=None, action_type=None,
                 action_details=None, location_id=None, timestamp=None, ip_address=None):
        self.id = id or str(uuid.uuid4())
        self.user_id = user_id
        self.board_id = board_id
        self.action_type = action_type
        self.action_details = action_details if isinstance(action_details, dict) else json.loads(action_details) if action_details else {}
        self.location_id = location_id
        self.timestamp = timestamp or datetime.utcnow()
        self.ip_address = ip_address
    
    @classmethod
    def find_by_id(cls, log_id):
        """Find an activity log by ID"""
        query = """
            SELECT id, user_id, board_id, action_type, action_details, location_id,
                   timestamp, ip_address
            FROM activity_log
            WHERE id = %s
        """
        result = db.execute_query(query, (log_id,), fetch_one=True)
        if result:
            if isinstance(result.get('action_details'), str):
                result['action_details'] = json.loads(result['action_details'])
            return cls(**result)
        return None
    
    @classmethod
    def find_by_location(cls, location_id, limit=100):
        """Find activity logs for a location"""
        query = """
            SELECT id, user_id, board_id, action_type, action_details, location_id,
                   timestamp, ip_address
            FROM activity_log
            WHERE location_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        results = db.execute_query(query, (location_id, limit), fetch_all=True)
        if results:
            for result in results:
                if isinstance(result.get('action_details'), str):
                    result['action_details'] = json.loads(result['action_details'])
            return [cls(**row) for row in results]
        return []
    
    @classmethod
    def find_by_user(cls, user_id, limit=50):
        """Find activity logs for a user"""
        query = """
            SELECT id, user_id, board_id, action_type, action_details, location_id,
                   timestamp, ip_address
            FROM activity_log
            WHERE user_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        results = db.execute_query(query, (user_id, limit), fetch_all=True)
        if results:
            for result in results:
                if isinstance(result.get('action_details'), str):
                    result['action_details'] = json.loads(result['action_details'])
            return [cls(**row) for row in results]
        return []
    
    @classmethod
    def find_by_board(cls, board_id, limit=50):
        """Find activity logs for a board"""
        query = """
            SELECT id, user_id, board_id, action_type, action_details, location_id,
                   timestamp, ip_address
            FROM activity_log
            WHERE board_id = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        results = db.execute_query(query, (board_id, limit), fetch_all=True)
        if results:
            for result in results:
                if isinstance(result.get('action_details'), str):
                    result['action_details'] = json.loads(result['action_details'])
            return [cls(**row) for row in results]
        return []
    
    def save(self):
        """Save activity log to database"""
        query = """
            INSERT INTO activity_log (id, user_id, board_id, action_type, action_details,
                                   location_id, timestamp, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        action_details_json = json.dumps(self.action_details) if self.action_details else None
        db.execute_query(query, (self.id, self.user_id, self.board_id, self.action_type,
                                action_details_json, self.location_id, self.timestamp,
                                self.ip_address))
    
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
            'action_details': self.action_details,
            'location_id': self.location_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'ip_address': self.ip_address
        }
