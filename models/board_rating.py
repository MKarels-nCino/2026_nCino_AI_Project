"""Board rating model - Represents a board rating and review using SQLAlchemy"""
import uuid
from datetime import datetime
from database import db


class BoardRating(db.Model):
    """Represents a rating and review for a board"""
    __tablename__ = 'board_ratings'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    board_id = db.Column(db.String(36), db.ForeignKey('boards.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    checkout_id = db.Column(db.String(36), db.ForeignKey('checkouts.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Unique constraint: one rating per user per checkout
    __table_args__ = (db.UniqueConstraint('board_id', 'user_id', 'checkout_id', name='unique_user_board_checkout_rating'),)
    
    def __init__(self, id=None, board_id=None, user_id=None, checkout_id=None,
                 rating=None, review=None, created_at=None, updated_at=None):
        if id:
            self.id = id
        self.board_id = board_id
        self.user_id = user_id
        self.checkout_id = checkout_id
        self.rating = rating
        self.review = review
        if created_at:
            self.created_at = created_at
        if updated_at:
            self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, rating_id):
        """Find a rating by ID"""
        return cls.query.get(rating_id)
    
    @classmethod
    def find_by_board(cls, board_id):
        """Find all ratings for a board"""
        return cls.query.filter_by(board_id=board_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def find_by_user(cls, user_id):
        """Find all ratings by a user"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def find_by_checkout(cls, checkout_id):
        """Find rating for a specific checkout"""
        return cls.query.filter_by(checkout_id=checkout_id).first()
    
    @classmethod
    def get_average_rating(cls, board_id):
        """Get average rating for a board"""
        from sqlalchemy import func
        result = cls.query.filter_by(board_id=board_id).with_entities(
            func.avg(cls.rating).label('avg_rating'),
            func.count(cls.id).label('count')
        ).first()
        
        if result and result.avg_rating:
            return {
                'average': float(result.avg_rating),
                'count': result.count
            }
        return {'average': 0.0, 'count': 0}
    
    def save(self):
        """Save rating to database"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'board_id': self.board_id,
            'user_id': self.user_id,
            'checkout_id': self.checkout_id,
            'rating': self.rating,
            'review': self.review,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<BoardRating {self.rating} stars for board {self.board_id}>'