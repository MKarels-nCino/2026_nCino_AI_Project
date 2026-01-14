"""Damage report model - Represents a board damage report using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db
from utils.constants import (
    DAMAGE_STATUS_NEW, DAMAGE_STATUS_IN_REPAIR, DAMAGE_STATUS_REPLACED,
    DAMAGE_SEVERITY_MINOR, DAMAGE_SEVERITY_MODERATE, DAMAGE_SEVERITY_SEVERE
)


class DamageReport(db.Model):
    """Represents a damage report for a board"""
    __tablename__ = 'damage_reports'
    
    STATUS_NEW = DAMAGE_STATUS_NEW
    STATUS_IN_REPAIR = DAMAGE_STATUS_IN_REPAIR
    STATUS_REPLACED = DAMAGE_STATUS_REPLACED
    
    SEVERITY_MINOR = DAMAGE_SEVERITY_MINOR
    SEVERITY_MODERATE = DAMAGE_SEVERITY_MODERATE
    SEVERITY_SEVERE = DAMAGE_SEVERITY_SEVERE
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    checkout_id = db.Column(db.String(36), db.ForeignKey('checkouts.id', ondelete='SET NULL'), nullable=True)
    board_id = db.Column(db.String(36), db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False)
    reported_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    description = db.Column(db.Text, nullable=True)
    severity = db.Column(db.String(50), default=DAMAGE_SEVERITY_MODERATE, nullable=False)
    status = db.Column(db.String(50), default=DAMAGE_STATUS_NEW, nullable=False)
    admin_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, id=None, checkout_id=None, board_id=None, reported_by=None,
                 description=None, severity=None, status=None, admin_notes=None,
                 created_at=None, updated_at=None):
        if id:
            self.id = id
        self.checkout_id = checkout_id
        self.board_id = board_id
        self.reported_by = reported_by
        self.description = description
        self.severity = severity or self.SEVERITY_MODERATE
        self.status = status or self.STATUS_NEW
        self.admin_notes = admin_notes
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, report_id):
        """Find a damage report by ID"""
        return cls.query.get(report_id)
    
    @classmethod
    def find_by_board(cls, board_id):
        """Find all damage reports for a board"""
        return cls.query.filter_by(board_id=board_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def find_by_status(cls, status):
        """Find damage reports by status"""
        return cls.query.filter_by(status=status).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def find_by_location(cls, location_id, status=None):
        """Find damage reports at a location"""
        from models.board import Board
        query = cls.query.join(Board).filter(Board.location_id == location_id)
        if status:
            query = query.filter(cls.status == status)
        return query.order_by(cls.created_at.desc()).all()
    
    def save(self):
        """Save damage report to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def update_status(self, new_status, admin_notes=None):
        """Update damage report status"""
        self.status = new_status
        if admin_notes:
            self.admin_notes = admin_notes
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'checkout_id': self.checkout_id,
            'board_id': self.board_id,
            'reported_by': self.reported_by,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<DamageReport {self.id} - {self.status}>'