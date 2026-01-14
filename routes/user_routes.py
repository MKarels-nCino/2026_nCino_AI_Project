"""User-facing routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from models.board import Board
from models.checkout import Checkout
from models.reservation import Reservation
from models.location import Location
from services.checkout_service import CheckoutService
from services.reservation_service import ReservationService
from services.timezone_service import TimezoneService
import logging

logger = logging.getLogger(__name__)

user_routes = Blueprint('user_routes', __name__)
checkout_service = CheckoutService()
reservation_service = ReservationService()
timezone_service = TimezoneService()


def get_selected_location_id():
    """Get the currently selected location ID from session, or default to user's location"""
    location_id = session.get('selected_location_id')
    if not location_id and current_user.is_authenticated:
        # Use user's default location if set, otherwise get first location
        location_id = current_user.location_id
        if not location_id:
            first_location = Location.find_all()
            if first_location:
                location_id = first_location[0].id
        # Always save to session so it persists
        if location_id:
            session['selected_location_id'] = location_id
    return location_id


@user_routes.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    from datetime import datetime, timedelta
    from models.board import Board
    import pytz
    
    location_id = get_selected_location_id()
    
    # Ensure we always have a location selected
    if not location_id:
        all_locations = Location.find_all()
        if all_locations:
            location_id = all_locations[0].id
            session['selected_location_id'] = location_id
    
    # Get all locations for the selector
    all_locations = Location.find_all()
    
    # Get selected date, hour, and duration from request (if provided)
    # Also check session for previously selected values
    selected_date = request.args.get('selected_date') or session.get('checkout_date')
    selected_hour = request.args.get('selected_hour') or session.get('checkout_hour')
    selected_duration = request.args.get('selected_duration') or session.get('checkout_duration', '1')
    selected_datetime_utc = None
    
    # Default to next day at 8 AM if not provided
    if not selected_date or not selected_hour:
        if location_id:
            tz = timezone_service.get_location_timezone(location_id)
            now_local = timezone_service.now_in_location(location_id)
            next_day = now_local + timedelta(days=1)
            next_day_8am = next_day.replace(hour=8, minute=0, second=0, microsecond=0)
            selected_date = next_day_8am.strftime('%Y-%m-%d')
            selected_hour = '8'
            selected_duration = '1'
    
    # Save selected values to session for use in cart
    if selected_date and selected_hour:
        session['checkout_date'] = selected_date
        session['checkout_hour'] = selected_hour
        session['checkout_duration'] = selected_duration
        session.permanent = True
    
    if selected_date and selected_hour:
        try:
            # Parse date and hour (hour is 0-23)
            hour = int(selected_hour)
            # Create datetime with hour only (minutes = 0)
            selected_datetime_local = datetime.strptime(f"{selected_date} {hour:02d}:00", '%Y-%m-%d %H:%M')
            # Convert to UTC using location timezone
            if location_id:
                tz = timezone_service.get_location_timezone(location_id)
                selected_datetime_local = tz.localize(selected_datetime_local)
                selected_datetime_utc = selected_datetime_local.astimezone(pytz.UTC)
        except (ValueError, TypeError):
            selected_datetime_utc = None
    
    # Get all boards for selected location (not just available)
    all_boards = Board.find_by_location(location_id) if location_id else []
    
    # Get duration as integer for availability check
    duration_hours = int(selected_duration) if selected_duration else 1
    
    # Check availability for each board at selected datetime
    available_boards = []
    for board in all_boards:
        if selected_datetime_utc:
            is_available, reason = board.is_available_at_datetime(selected_datetime_utc, duration_hours)
            board.availability_at_time = is_available
            board.availability_reason = reason if not is_available else None
        else:
            # If no datetime selected, use current availability
            board.availability_at_time = board.is_available()
            board.availability_reason = None if board.is_available() else "Not available"
        
        available_boards.append(board)
    
    # Get all active checkouts (across all locations)
    # Combine everything into reservations section:
    # - Scheduled: checkout_time > now
    # - In Use: checkout_time <= now
    all_active_checkouts = Checkout.find_active_by_user(current_user.id)
    now = datetime.utcnow()
    
    # Get actual reservations
    reservations = Reservation.find_by_user(current_user.id)
    
    # Combine all checkouts and reservations into one list for display
    all_items = []
    
    # Add checkouts (both scheduled and in use)
    for checkout in all_active_checkouts:
        board = Board.find_by_id(checkout.board_id)
        checkout.board = board
        # Get location for checkout
        if board:
            location = Location.find_by_id(board.location_id)
            checkout.location = location
        checkout.is_checkout = True
        checkout.status = 'scheduled' if checkout.checkout_time > now else 'in_use'
        all_items.append(checkout)
    
    # Add actual reservations (only pending/available, not cancelled)
    for reservation in reservations:
        # Skip cancelled reservations
        if reservation.status == Reservation.STATUS_CANCELLED:
            continue
        board = Board.find_by_id(reservation.board_id)
        reservation.board = board
        # Get location from board
        if board:
            location = Location.find_by_id(board.location_id)
            reservation.location = location
        reservation.is_checkout = False
        all_items.append(reservation)
    
    # Sort by date (scheduled first, then in use, then reservations)
    def sort_key(x):
        if hasattr(x, 'is_checkout') and x.is_checkout:
            if x.checkout_time > now:
                return (0, x.checkout_time)  # Scheduled first
            else:
                return (1, x.checkout_time)  # In use second
        else:
            unlock = x.unlock_time if hasattr(x, 'unlock_time') else datetime.min
            return (2, unlock)  # Reservations third
    
    all_items.sort(key=sort_key)
    
    # Get current location object
    current_location = Location.find_by_id(location_id) if location_id else None
    
    return render_template('user/dashboard.html',
                         available_boards=available_boards,
                         all_items=all_items,
                         all_locations=all_locations,
                         current_location=current_location,
                         selected_location_id=location_id,
                         selected_date=selected_date,
                         selected_hour=selected_hour,
                         selected_duration=selected_duration,
                         now=now,
                         timezone_service=timezone_service)


@user_routes.route('/switch-location', methods=['POST'])
@login_required
def switch_location():
    """Switch the selected location"""
    location_id = request.form.get('location_id') or request.json.get('location_id')
    if location_id:
        # Verify location exists
        location = Location.find_by_id(location_id)
        if location:
            session['selected_location_id'] = location_id
        else:
            flash('Location not found', 'error')
    else:
        flash('No location selected', 'error')
    
    if request.is_json:
        return jsonify({'success': True, 'location_id': location_id})
    return redirect(url_for('user_routes.dashboard'))


@user_routes.route('/boards')
@login_required
def boards():
    """View all boards at location"""
    location_id = get_selected_location_id()
    boards_list = Board.find_by_location(location_id) if location_id else []
    all_locations = Location.find_all()
    current_location = Location.find_by_id(location_id) if location_id else None
    
    return render_template('user/boards.html', 
                         boards=boards_list,
                         all_locations=all_locations,
                         current_location=current_location,
                         selected_location_id=location_id)


@user_routes.route('/my-checkouts')
@login_required
def my_checkouts():
    """View user's reservations - all checkouts and reservations combined"""
    from models.board import Board
    from models.location import Location
    from datetime import datetime
    
    now = datetime.utcnow()
    
    # Get all active checkouts for user
    all_active_checkouts = Checkout.find_active_by_user(current_user.id)
    
    # Get all reservations for user
    reservations_list = Reservation.find_by_user(current_user.id)
    
    # Combine all checkouts and reservations into one list for display
    all_items = []
    
    # Add checkouts (both scheduled and in use)
    for checkout in all_active_checkouts:
        if checkout.status == Checkout.STATUS_CANCELLED:
            continue
        board = Board.find_by_id(checkout.board_id)
        checkout.board = board
        if board:
            location = Location.find_by_id(board.location_id)
            checkout.location = location
        checkout.is_checkout = True
        checkout.display_status = 'scheduled' if checkout.checkout_time > now else 'in_use'
        all_items.append(checkout)
    
    # Add actual reservations
    for reservation in reservations_list:
        if reservation.status == Reservation.STATUS_CANCELLED:
            continue
        board = Board.find_by_id(reservation.board_id)
        reservation.board = board
        if board:
            location = Location.find_by_id(board.location_id)
            reservation.location = location
        reservation.is_checkout = False
        all_items.append(reservation)
    
    # Sort by date
    def sort_key(x):
        if x.is_checkout:
            return x.checkout_time
        return x.unlock_time
    
    all_items.sort(key=sort_key)
    
    return render_template('user/my_checkouts.html', 
                          all_items=all_items,
                          timezone_service=timezone_service)


@user_routes.route('/reservations')
@login_required
def reservations():
    """View user's reservations"""
    reservations_list = Reservation.find_by_user(current_user.id)
    return render_template('user/reservations.html', reservations=reservations_list)


@user_routes.route('/my-account', methods=['GET', 'POST'])
@login_required
def my_account():
    """View and edit user account settings"""
    from models.location import Location
    from werkzeug.security import check_password_hash, generate_password_hash
    from database import db
    
    all_locations = Location.find_all()
    message = None
    error = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            # Update profile info
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            location_id = request.form.get('location_id')
            
            if full_name and email:
                current_user.full_name = full_name
                current_user.email = email
                if location_id:
                    current_user.location_id = location_id
                db.session.commit()
                message = "Profile updated successfully!"
            else:
                error = "Name and email are required."
        
        elif action == 'change_password':
            # Change password
            current_password = request.form.get('current_password', '')
            new_password = request.form.get('new_password', '')
            confirm_password = request.form.get('confirm_password', '')
            
            if not current_password or not new_password or not confirm_password:
                error = "All password fields are required."
            elif new_password != confirm_password:
                error = "New passwords do not match."
            elif len(new_password) < 6:
                error = "New password must be at least 6 characters."
            elif not check_password_hash(current_user.password_hash, current_password):
                error = "Current password is incorrect."
            else:
                current_user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                message = "Password changed successfully!"
    
    return render_template('user/my_account.html',
                          all_locations=all_locations,
                          message=message,
                          error=error)
