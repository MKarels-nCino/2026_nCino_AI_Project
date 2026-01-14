"""Damage report model - Represents a board damage report"""
import uuid
from datetime import datetime
from database import db
from utils.constants import (
    DAMAGE_STATUS_NEW, DAMAGE_STATUS_IN_REPAIR, DAMAGE_STATUS_REPLACED,
    DAMAGE_SEVERITY_MINOR, DAMAGE_SEVERITY_MODERATE, DAMAGE_SEVERITY_SEVERE
)


class DamageReport:
    """Represents a damage report for a board"""
    
    STATUS_NEW = DAMAGE_STATUS_NEW
    STATUS_IN_REPAIR = DAMAGE_STATUS_IN_REPAIR
    STATUS_REPLACED = DAMAGE_STATUS_REPLACED
    
    SEVERITY_MINOR = DAMAGE_SEVERITY_MINOR
    SEVERITY_MODERATE = DAMAGE_SEVERITY_MODERATE
    SEVERITY_SEVERE = DAMAGE_SEVERITY_SEVERE
    
    def __init__(self, id=None, checkout_id=None, board_id=None, reported_by=None,
                 description=None, severity=None, status=None, admin_notes=None,
                 created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.checkout_id = checkout_id
        self.board_id = board_id
        self.reported_by = reported_by
        self.description = description
        self.severity = severity or self.SEVERITY_MODERATE
        self.status = status or self.STATUS_NEW
        self.admin_notes = admin_notes
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, report_id):
        """Find a damage report by ID"""
        query = """
            SELECT id, checkout_id, board_id, reported_by, description, severity,
                   status, admin_notes, created_at, updated_at
            FROM damage_reports
            WHERE id = %s
        """
        result = db.execute_query(query, (report_id,), fetch_one=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def find_by_board(cls, board_id):
        """Find all damage reports for a board"""
        query = """
            SELECT id, checkout_id, board_id, reported_by, description, severity,
                   status, admin_notes, created_at, updated_at
            FROM damage_reports
            WHERE board_id = %s
            ORDER BY created_at DESC
        """
        results = db.execute_query(query, (board_id,), fetch_all=True)
        return [cls(**row) for row in results] if results else []
    
    @classmethod
    def find_by_status(cls, status):
        """Find damage reports by status"""
        query = """
            SELECT id, checkout_id, board_id, reported_by, description, severity,
                   status, admin_notes, created_at, updated_at
            FROM damage_reports
            WHERE status = %s
            ORDER BY created_at DESC
        """
        results = db.execute_query(query, (status,), fetch_all=True)
        return [cls(**row) for row in results] if results else []
    
    @classmethod
    def find_by_location(cls, location_id, status=None):
        """Find damage reports at a location"""
        if status:
            query = """
                SELECT dr.id, dr.checkout_id, dr.board_id, dr.reported_by, dr.description,
                       dr.severity, dr.status, dr.admin_notes, dr.created_at, dr.updated_at
                FROM damage_reports dr
                JOIN boards b ON dr.board_id = b.id
                WHERE b.location_id = %s AND dr.status = %s
                ORDER BY dr.created_at DESC
            """
            results = db.execute_query(query, (location_id, status), fetch_all=True)
        else:
            query = """
                SELECT dr.id, dr.checkout_id, dr.board_id, dr.reported_by, dr.description,
                       dr.severity, dr.status, dr.admin_notes, dr.created_at, dr.updated_at
                FROM damage_reports dr
                JOIN boards b ON dr.board_id = b.id
                WHERE b.location_id = %s
                ORDER BY dr.created_at DESC
            """
            results = db.execute_query(query, (location_id,), fetch_all=True)
        return [cls(**row) for row in results] if results else []
    
    def save(self):
        """Save damage report to database (insert or update)"""
        if self.find_by_id(self.id):
            # Update existing
            query = """
                UPDATE damage_reports
                SET checkout_id = %s, board_id = %s, reported_by = %s, description = %s,
                    severity = %s, status = %s, admin_notes = %s
                WHERE id = %s
            """
            db.execute_query(query, (self.checkout_id, self.board_id, self.reported_by,
                                   self.description, self.severity, self.status,
                                   self.admin_notes, self.id))
        else:
            # Insert new
            query = """
                INSERT INTO damage_reports (id, checkout_id, board_id, reported_by,
                                          description, severity, status, admin_notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query, (self.id, self.checkout_id, self.board_id,
                                    self.reported_by, self.description, self.severity,
                                    self.status, self.admin_notes))
    
    def update_status(self, new_status, admin_notes=None):
        """Update damage report status"""
        query = """
            UPDATE damage_reports
            SET status = %s, admin_notes = %s
            WHERE id = %s
        """
        db.execute_query(query, (new_status, admin_notes, self.id))
        self.status = new_status
        if admin_notes:
            self.admin_notes = admin_notes
    
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
