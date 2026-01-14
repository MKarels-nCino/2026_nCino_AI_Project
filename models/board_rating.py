"""Board rating model - Represents a board rating and review"""
import uuid
from datetime import datetime
from database import db


class BoardRating:
    """Represents a rating and review for a board"""
    
    def __init__(self, id=None, board_id=None, user_id=None, checkout_id=None,
                 rating=None, review=None, created_at=None, updated_at=None):
        self.id = id or str(uuid.uuid4())
        self.board_id = board_id
        self.user_id = user_id
        self.checkout_id = checkout_id
        self.rating = rating
        self.review = review
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def find_by_id(cls, rating_id):
        """Find a rating by ID"""
        query = """
            SELECT id, board_id, user_id, checkout_id, rating, review, created_at, updated_at
            FROM board_ratings
            WHERE id = %s
        """
        result = db.execute_query(query, (rating_id,), fetch_one=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def find_by_board(cls, board_id):
        """Find all ratings for a board"""
        query = """
            SELECT id, board_id, user_id, checkout_id, rating, review, created_at, updated_at
            FROM board_ratings
            WHERE board_id = %s
            ORDER BY created_at DESC
        """
        results = db.execute_query(query, (board_id,), fetch_all=True)
        return [cls(**row) for row in results] if results else []
    
    @classmethod
    def find_by_user(cls, user_id):
        """Find all ratings by a user"""
        query = """
            SELECT id, board_id, user_id, checkout_id, rating, review, created_at, updated_at
            FROM board_ratings
            WHERE user_id = %s
            ORDER BY created_at DESC
        """
        results = db.execute_query(query, (user_id,), fetch_all=True)
        return [cls(**row) for row in results] if results else []
    
    @classmethod
    def find_by_checkout(cls, checkout_id):
        """Find rating for a specific checkout"""
        query = """
            SELECT id, board_id, user_id, checkout_id, rating, review, created_at, updated_at
            FROM board_ratings
            WHERE checkout_id = %s
        """
        result = db.execute_query(query, (checkout_id,), fetch_one=True)
        if result:
            return cls(**result)
        return None
    
    @classmethod
    def get_average_rating(cls, board_id):
        """Get average rating for a board"""
        query = """
            SELECT AVG(rating) as avg_rating, COUNT(*) as count
            FROM board_ratings
            WHERE board_id = %s
        """
        result = db.execute_query(query, (board_id,), fetch_one=True)
        if result and result.get('avg_rating'):
            return {
                'average': float(result['avg_rating']),
                'count': result['count']
            }
        return {'average': 0.0, 'count': 0}
    
    def save(self):
        """Save rating to database (insert or update)"""
        if self.find_by_id(self.id):
            # Update existing
            query = """
                UPDATE board_ratings
                SET rating = %s, review = %s
                WHERE id = %s
            """
            db.execute_query(query, (self.rating, self.review, self.id))
        else:
            # Insert new (or update if unique constraint violation)
            query = """
                INSERT INTO board_ratings (id, board_id, user_id, checkout_id, rating, review)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (board_id, user_id, checkout_id)
                DO UPDATE SET rating = EXCLUDED.rating, review = EXCLUDED.review
            """
            db.execute_query(query, (self.id, self.board_id, self.user_id,
                                    self.checkout_id, self.rating, self.review))
    
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
