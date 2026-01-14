"""Decorators for authentication and authorization"""
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from flask_login import current_user
from models.user import User


def login_required(f):
    """Decorator to require user login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('auth_routes.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            if request.is_json:
                return jsonify({'error': 'Admin access required'}), 403
            return redirect(url_for('user_routes.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


def require_location_access(f):
    """Decorator to ensure user can only access their location's data"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_location_id = current_user.location_id
        
        # Check if location_id is in kwargs and matches user's location
        if 'location_id' in kwargs:
            if str(kwargs['location_id']) != str(user_location_id):
                if request.is_json:
                    return jsonify({'error': 'Access denied to this location'}), 403
                return redirect(url_for('user_routes.dashboard'))
        
        # For admin users, they can access their assigned location
        if current_user.is_admin():
            # Admin can only manage their assigned location
            pass
        
        return f(*args, **kwargs)
    return decorated_function
