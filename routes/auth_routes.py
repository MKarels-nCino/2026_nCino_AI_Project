"""Authentication routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_service import AuthService
from models.user import User
from utils.constants import (
    MSG_LOGIN_SUCCESS, MSG_LOGIN_FAILED, MSG_REGISTRATION_SUCCESS,
    MSG_REGISTRATION_FAILED, MSG_LOGOUT_SUCCESS, USER_ROLE_USER
)
import logging

logger = logging.getLogger(__name__)

auth_routes = Blueprint('auth_routes', __name__)
auth_service = AuthService()


@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('user_routes.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user, _ = auth_service.sign_in(email, password)
            login_user(user, remember=True)
            flash(MSG_LOGIN_SUCCESS, 'success')
            return redirect(url_for('user_routes.dashboard'))
        except Exception as e:
            flash(f'{MSG_LOGIN_FAILED}: {str(e)}', 'error')
            logger.error(f"Login failed for {email}: {e}")
    
    return render_template('auth/login.html')


@auth_routes.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('user_routes.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        location_id = request.form.get('location_id')
        role = request.form.get('role', USER_ROLE_USER)
        
        try:
            user = auth_service.sign_up(email, password, full_name, location_id, role)
            login_user(user, remember=True)
            flash(MSG_REGISTRATION_SUCCESS, 'success')
            return redirect(url_for('user_routes.dashboard'))
        except Exception as e:
            flash(f'{MSG_REGISTRATION_FAILED}: {str(e)}', 'error')
            logger.error(f"Registration failed for {email}: {e}")
    
    # Get locations for registration form
    from models.location import Location
    locations = Location.find_all()
    
    return render_template('auth/register.html', locations=locations)


@auth_routes.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash(MSG_LOGOUT_SUCCESS, 'info')
    return redirect(url_for('auth_routes.login'))
