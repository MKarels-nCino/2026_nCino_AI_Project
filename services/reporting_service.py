"""Reporting service - Handles analytics and reporting"""
from models.board import Board
from models.checkout import Checkout
from models.board_rating import BoardRating
from models.user import User
from utils.constants import CHECKOUT_STATUS_RETURNED
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ReportingService:
    """Service for generating reports and analytics"""
    
    def __init__(self):
        pass
    
    def get_favorite_boards(self, location_id, limit=10):
        """
        Get most checked-out boards (favorites)
        Returns: List of dicts with board info and checkout count
        """
        query = """
            SELECT b.id, b.name, b.brand, b.size, COUNT(c.id) as checkout_count
            FROM boards b
            LEFT JOIN checkouts c ON b.id = c.board_id AND c.status = %s
            WHERE b.location_id = %s
            GROUP BY b.id, b.name, b.brand, b.size
            ORDER BY checkout_count DESC
            LIMIT %s
        """
        from database import db
        results = db.execute_query(query, (CHECKOUT_STATUS_RETURNED, location_id, limit), fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    def get_usage_per_user(self, location_id, start_date=None, end_date=None):
        """
        Get usage statistics per user
        Returns: List of dicts with user info and checkout count
        """
        query = """
            SELECT u.id, u.full_name, u.email, COUNT(c.id) as checkout_count
            FROM users u
            LEFT JOIN checkouts c ON u.id = c.user_id
            WHERE u.location_id = %s
        """
        params = [location_id]
        
        if start_date:
            query += " AND c.checkout_time >= %s"
            params.append(start_date)
        if end_date:
            query += " AND c.checkout_time <= %s"
            params.append(end_date)
        
        query += " GROUP BY u.id, u.full_name, u.email ORDER BY checkout_count DESC"
        
        from database import db
        results = db.execute_query(query, tuple(params), fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    def get_usage_per_location(self, start_date=None, end_date=None):
        """
        Get usage statistics per location
        Returns: List of dicts with location info and checkout count
        """
        query = """
            SELECT l.id, l.name, COUNT(c.id) as checkout_count
            FROM locations l
            LEFT JOIN boards b ON l.id = b.location_id
            LEFT JOIN checkouts c ON b.id = c.board_id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND c.checkout_time >= %s"
            params.append(start_date)
        if end_date:
            query += " AND c.checkout_time <= %s"
            params.append(end_date)
        
        query += " GROUP BY l.id, l.name ORDER BY checkout_count DESC"
        
        from database import db
        results = db.execute_query(query, tuple(params), fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    def get_usage_trends(self, location_id, days=30):
        """
        Get usage trends over time
        Returns: List of dicts with date and checkout count
        """
        query = """
            SELECT DATE(c.checkout_time) as date, COUNT(*) as checkout_count
            FROM checkouts c
            JOIN boards b ON c.board_id = b.id
            WHERE b.location_id = %s
            AND c.checkout_time >= %s
            GROUP BY DATE(c.checkout_time)
            ORDER BY date ASC
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        from database import db
        results = db.execute_query(query, (location_id, start_date), fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    def get_seasonal_trends(self, location_id, year=None):
        """
        Get seasonal usage trends
        Returns: Dict with seasonal breakdown
        """
        if year is None:
            year = datetime.utcnow().year
        
        query = """
            SELECT 
                CASE 
                    WHEN EXTRACT(MONTH FROM c.checkout_time) IN (12, 1, 2) THEN 'Winter'
                    WHEN EXTRACT(MONTH FROM c.checkout_time) IN (3, 4, 5) THEN 'Spring'
                    WHEN EXTRACT(MONTH FROM c.checkout_time) IN (6, 7, 8) THEN 'Summer'
                    ELSE 'Fall'
                END as season,
                COUNT(*) as checkout_count
            FROM checkouts c
            JOIN boards b ON c.board_id = b.id
            WHERE b.location_id = %s
            AND EXTRACT(YEAR FROM c.checkout_time) = %s
            GROUP BY season
            ORDER BY season
        """
        # Note: Year is passed as parameter, CASE statements are safe (not user input)
        
        from database import db
        results = db.execute_query(query, (location_id, year), fetch_all=True)
        return {row['season']: row['checkout_count'] for row in results} if results else {}
    
    def get_peak_usage_times(self, location_id, days=30):
        """
        Get peak usage times (hour of day)
        Returns: List of dicts with hour and checkout count
        """
        query = """
            SELECT EXTRACT(HOUR FROM c.checkout_time) as hour, COUNT(*) as checkout_count
            FROM checkouts c
            JOIN boards b ON c.board_id = b.id
            WHERE b.location_id = %s
            AND c.checkout_time >= %s
            GROUP BY EXTRACT(HOUR FROM c.checkout_time)
            ORDER BY hour ASC
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        from database import db
        results = db.execute_query(query, (location_id, start_date), fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    def get_damage_frequency_by_board(self, location_id):
        """
        Get damage frequency statistics by board
        Returns: List of dicts with board info and damage count
        """
        query = """
            SELECT b.id, b.name, b.brand, COUNT(dr.id) as damage_count
            FROM boards b
            LEFT JOIN damage_reports dr ON b.id = dr.board_id
            WHERE b.location_id = %s
            GROUP BY b.id, b.name, b.brand
            HAVING COUNT(dr.id) > 0
            ORDER BY damage_count DESC
        """
        
        from database import db
        results = db.execute_query(query, (location_id,), fetch_all=True)
        return [dict(row) for row in results] if results else []
    
    def get_board_ratings_summary(self, location_id):
        """
        Get ratings summary for all boards at location
        Returns: List of dicts with board info and rating stats
        """
        query = """
            SELECT 
                b.id, 
                b.name, 
                b.brand,
                AVG(br.rating) as avg_rating,
                COUNT(br.id) as rating_count
            FROM boards b
            LEFT JOIN board_ratings br ON b.id = br.board_id
            WHERE b.location_id = %s
            GROUP BY b.id, b.name, b.brand
            HAVING COUNT(br.id) > 0
            ORDER BY avg_rating DESC, rating_count DESC
        """
        
        from database import db
        results = db.execute_query(query, (location_id,), fetch_all=True)
        return [dict(row) for row in results] if results else []
