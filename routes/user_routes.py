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
    location_id = get_selected_location_id()
    
    # Ensure we always have a location selected
    if not location_id:
        all_locations = Location.find_all()
        if all_locations:
            location_id = all_locations[0].id
            session['selected_location_id'] = location_id
    
    # Get all locations for the selector
    all_locations = Location.find_all()
    
    # Get available boards for selected location
    available_boards = Board.find_available(location_id) if location_id else []
    
    # Get user's active checkouts (across all locations)
    active_checkouts = Checkout.find_active_by_user(current_user.id)
    
    # Get user's reservations (across all locations)
    reservations = Reservation.find_by_user(current_user.id)
    
    # Get current location object
    current_location = Location.find_by_id(location_id) if location_id else None
    
    return render_template('user/dashboard.html',
                         available_boards=available_boards,
                         active_checkouts=active_checkouts,
                         reservations=reservations,
                         all_locations=all_locations,
                         current_location=current_location,
                         selected_location_id=location_id)


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
    """View user's checkout history"""
    from models.board import Board
    checkouts = Checkout.find_by_user(current_user.id, limit=50)
    # Get board info for each checkout
    for checkout in checkouts:
        board = Board.find_by_id(checkout.board_id)
        checkout.board = board
    return render_template('user/my_checkouts.html', checkouts=checkouts)


@user_routes.route('/reservations')
@login_required
def reservations():
    """View user's reservations"""
    reservations_list = Reservation.find_by_user(current_user.id)
    return render_template('user/reservations.html', reservations=reservations_list)
