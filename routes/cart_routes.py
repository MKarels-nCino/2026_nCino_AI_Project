"""Cart routes - Shopping cart functionality"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from models.board import Board
from models.checkout import Checkout
from models.location import Location
from models.activity_log import ActivityLog
from services.checkout_service import CheckoutService
from services.timezone_service import TimezoneService
from database import db
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

cart_routes = Blueprint('cart_routes', __name__)
checkout_service = CheckoutService()
timezone_service = TimezoneService()


def get_cart():
    """Get cart from session"""
    return session.get('cart', [])


def save_cart(cart):
    """Save cart to session"""
    session['cart'] = cart
    session.permanent = True


def get_selected_location_id():
    """Get the currently selected location ID from session"""
    location_id = session.get('selected_location_id')
    if not location_id and current_user.is_authenticated:
        location_id = current_user.location_id
        if not location_id:
            first_location = Location.find_all()
            if first_location:
                location_id = first_location[0].id
        if location_id:
            session['selected_location_id'] = location_id
    return location_id


@cart_routes.route('/cart')
@login_required
def view_cart():
    """View shopping cart"""
    cart = get_cart()
    location_id = get_selected_location_id()
    
    if not location_id:
        flash('Please select a location first', 'error')
        return redirect(url_for('user_routes.dashboard'))
    
    # Get board details for items in cart
    cart_items = []
    for board_id in cart:
        board = Board.find_by_id(board_id)
        if board and board.location_id == location_id and board.is_available():
            cart_items.append(board)
    
    # Filter out boards that are no longer available or from different location
    valid_cart = [item.id for item in cart_items]
    if len(valid_cart) != len(cart):
        save_cart(valid_cart)
        if len(valid_cart) < len(cart):
            flash('Some boards were removed from your cart (no longer available)', 'warning')
    
    current_location = Location.find_by_id(location_id) if location_id else None
    
    # Get checkout details from session (set on dashboard)
    checkout_date = session.get('checkout_date')
    checkout_hour = session.get('checkout_hour')
    checkout_duration = session.get('checkout_duration', '1')
    
    # If not in session, default to next day at 8 AM
    if not checkout_date or not checkout_hour:
        if current_location:
            tz = timezone_service.get_location_timezone(location_id)
            now_local = timezone_service.now_in_location(location_id)
            next_day = now_local + timedelta(days=1)
            next_day_8am = next_day.replace(hour=8, minute=0, second=0, microsecond=0)
            checkout_date = next_day_8am.strftime('%Y-%m-%d')
            checkout_hour = '8'
            checkout_duration = '1'
        else:
            checkout_date = None
            checkout_hour = None
            checkout_duration = '1'
    
    return render_template('user/cart.html',
                         cart_items=cart_items,
                         current_location=current_location,
                         checkout_date=checkout_date,
                         checkout_hour=checkout_hour,
                         checkout_duration=checkout_duration)


@cart_routes.route('/cart/add/<board_id>', methods=['POST'])
@login_required
def add_to_cart(board_id):
    """Add board to cart"""
    location_id = get_selected_location_id()
    
    if not location_id:
        return jsonify({'success': False, 'error': 'No location selected'}), 400
    
    # Verify board exists and is available
    board = Board.find_by_id(board_id)
    if not board:
        return jsonify({'success': False, 'error': 'Board not found'}), 404
    
    if board.location_id != location_id:
        return jsonify({'success': False, 'error': 'Board not at selected location'}), 400
    
    if not board.is_available():
        return jsonify({'success': False, 'error': 'Board is not available'}), 400
    
    # Check for active checkout
    active_checkout = Checkout.find_active_by_board(board_id)
    if active_checkout:
        return jsonify({'success': False, 'error': 'Board is already checked out'}), 400
    
    # Get selected checkout date from session
    from models.reservation import Reservation
    from datetime import datetime
    
    selected_checkout_date_str = session.get('checkout_date')
    selected_checkout_date = None
    if selected_checkout_date_str:
        try:
            selected_checkout_date = datetime.strptime(selected_checkout_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Check for location mismatch with existing cart items (must be same location for same cart/day)
    cart = get_cart()
    if cart:
        for cart_board_id in cart:
            cart_board = Board.find_by_id(cart_board_id)
            if cart_board and cart_board.location_id != board.location_id:
                # Cart items from different location - not allowed (same checkout = same day = same location)
                cart_location = Location.find_by_id(cart_board.location_id)
                board_location = Location.find_by_id(board.location_id)
                return jsonify({
                    'success': False, 
                    'error': f'You have items in your cart from {cart_location.name if cart_location else "another location"}. Cart items must be from the same location. Please checkout or remove those items first.'
                }), 400
    
    # Check for date conflicts with existing scheduled checkouts from different locations
    # Allow different locations ONLY if dates are different
    active_checkouts = Checkout.find_active_by_user(current_user.id)
    for checkout in active_checkouts:
        checkout_board = Board.find_by_id(checkout.board_id)
        if checkout_board and checkout_board.location_id != board.location_id:
            # Different location - check if same date
            checkout_date = checkout.checkout_time.date() if checkout.checkout_time else None
            if selected_checkout_date and checkout_date and selected_checkout_date == checkout_date:
                checkout_location = Location.find_by_id(checkout_board.location_id)
                board_location = Location.find_by_id(board.location_id)
                return jsonify({
                    'success': False,
                    'error': f'You already have a reservation at {checkout_location.name if checkout_location else "another location"} on {selected_checkout_date.strftime("%b %d, %Y")}. You cannot reserve boards from different locations on the same day.'
                }), 400
    
    # Check for date conflicts with existing reservations from different locations
    reservations = Reservation.find_by_user(current_user.id)
    for reservation in reservations:
        if reservation.status in ['pending', 'available']:
            reservation_board = Board.find_by_id(reservation.board_id)
            if reservation_board and reservation_board.location_id != board.location_id:
                # Different location - check if same date
                reservation_date = reservation.unlock_time.date() if reservation.unlock_time else None
                if selected_checkout_date and reservation_date and selected_checkout_date == reservation_date:
                    reservation_location = Location.find_by_id(reservation_board.location_id)
                    board_location = Location.find_by_id(board.location_id)
                    return jsonify({
                        'success': False,
                        'error': f'You already have a reservation at {reservation_location.name if reservation_location else "another location"} on {selected_checkout_date.strftime("%b %d, %Y")}. You cannot reserve boards from different locations on the same day.'
                    }), 400
    
    # Add to cart
    if board_id not in cart:
        cart.append(board_id)
        save_cart(cart)
    
    return jsonify({
        'success': True,
        'message': 'Board added to cart',
        'cart_count': len(cart)
    })


@cart_routes.route('/cart/remove/<board_id>', methods=['POST'])
@login_required
def remove_from_cart(board_id):
    """Remove board from cart"""
    cart = get_cart()
    if board_id in cart:
        cart.remove(board_id)
        save_cart(cart)
    
    return jsonify({
        'success': True,
        'message': 'Board removed from cart',
        'cart_count': len(cart)
    })


@cart_routes.route('/cart/checkout', methods=['POST'])
@login_required
def checkout_cart():
    """Checkout all items in cart"""
    cart = get_cart()
    location_id = get_selected_location_id()
    
    if not cart:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400
    
    if not location_id:
        return jsonify({'success': False, 'error': 'No location selected'}), 400
    
    # Get checkout datetime and duration from request
    checkout_date = request.json.get('checkout_date')
    checkout_hour = request.json.get('checkout_hour')
    duration_hours = request.json.get('duration_hours', 1)  # Default to 1 hour
    
    if not checkout_date or not checkout_hour:
        return jsonify({'success': False, 'error': 'Checkout date and hour required'}), 400
    
    try:
        # Parse datetime (format: YYYY-MM-DD and hour 0-23)
        hour = int(checkout_hour)
        checkout_datetime_str = f"{checkout_date} {hour:02d}:00"
        checkout_datetime_local = datetime.strptime(checkout_datetime_str, '%Y-%m-%d %H:%M')
        
        # Convert to UTC for storage
        import pytz
        tz = timezone_service.get_location_timezone(location_id)
        checkout_datetime_local = tz.localize(checkout_datetime_local)
        checkout_datetime_utc = checkout_datetime_local.astimezone(pytz.UTC)
        
        # Calculate return time based on duration (hours)
        duration_hours = int(duration_hours)
        if duration_hours < 1:
            duration_hours = 1
        elif duration_hours > 24:
            duration_hours = 24
        
        expected_return_time = checkout_datetime_utc + timedelta(hours=duration_hours)
        
    except Exception as e:
        logger.error(f"Error parsing checkout datetime: {e}")
        return jsonify({'success': False, 'error': 'Invalid date/time format'}), 400
    
    # Checkout all boards
    checkouts = []
    errors = []
    
    # Use a transaction to ensure all-or-nothing checkout
    try:
        for board_id in cart:
            try:
                # Verify board is still available
                board = Board.find_by_id(board_id)
                if not board:
                    errors.append(f"Board {board_id} not found")
                    continue
                    
                if board.location_id != location_id:
                    errors.append(f"Board {board.name} is not at selected location")
                    continue
                    
                if not board.is_available():
                    errors.append(f"Board {board.name} is no longer available")
                    continue
                
                # Check for active checkout
                active_checkout = Checkout.find_active_by_board(board_id)
                if active_checkout:
                    errors.append(f"Board {board.name} is already checked out")
                    continue
                
                # Create checkout
                checkout = Checkout(
                    user_id=current_user.id,
                    board_id=board_id,
                    checkout_time=checkout_datetime_utc,
                    expected_return_time=expected_return_time,
                    status=Checkout.STATUS_ACTIVE
                )
                db.session.add(checkout)
                
                # Update board status
                board.status = Board.STATUS_CHECKED_OUT
                db.session.add(board)
                
                # Log activity
                try:
                    log = ActivityLog(
                        user_id=current_user.id,
                        board_id=board_id,
                        action_type=ActivityLog.ACTION_CHECKOUT,
                        action_details={
                            'checkout_id': checkout.id,
                            'expected_return_time': expected_return_time.isoformat(),
                            'is_weekend': is_weekend
                        },
                        location_id=location_id,
                        ip_address=request.remote_addr
                    )
                    db.session.add(log)
                except Exception as log_error:
                    logger.error(f"Error creating activity log: {log_error}")
                    import traceback
                    logger.error(traceback.format_exc())
                    # Don't fail checkout if logging fails
                
                checkouts.append(checkout)
                
            except Exception as e:
                logger.error(f"Error checking out board {board_id}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                errors.append(f"Error checking out board {board_id}: {str(e)}")
        
        # Commit all checkouts at once
        if checkouts:
            db.session.commit()
            # Refresh checkouts to get IDs
            for checkout in checkouts:
                db.session.refresh(checkout)
        else:
            db.session.rollback()
            
    except Exception as e:
        logger.error(f"Error during checkout transaction: {e}")
        import traceback
        logger.error(traceback.format_exc())
        db.session.rollback()
        if not errors:
            errors.append(f"Checkout failed: {str(e)}")
    
    # Clear cart
    save_cart([])
    
    if checkouts:
        return jsonify({
            'success': True,
            'message': f'Successfully checked out {len(checkouts)} board(s)',
            'checkouts': [c.to_dict() for c in checkouts],
            'errors': errors if errors else None
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Failed to checkout any boards',
            'errors': errors
        }), 400
