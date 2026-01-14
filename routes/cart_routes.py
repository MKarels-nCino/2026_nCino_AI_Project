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
import pytz

logger = logging.getLogger(__name__)

cart_routes = Blueprint('cart_routes', __name__)
checkout_service = CheckoutService()
timezone_service = TimezoneService()


def get_cart():
    """
    Get cart from session.
    Cart is a list of dicts: [{board_id, location_id, checkout_date, checkout_hour, duration_hours}, ...]
    """
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
    
    # Build cart items with full details
    cart_items = []
    valid_cart = []
    
    for item in cart:
        # Handle both old format (just board_id string) and new format (dict)
        if isinstance(item, str):
            board_id = item
            item_details = {
                'board_id': board_id,
                'location_id': get_selected_location_id(),
                'checkout_date': session.get('checkout_date', ''),
                'checkout_hour': session.get('checkout_hour', '8'),
                'duration_hours': session.get('checkout_duration', '1')
            }
        else:
            board_id = item.get('board_id')
            item_details = item
        
        board = Board.find_by_id(board_id)
        if board and board.is_available():
            location = Location.find_by_id(item_details.get('location_id'))
            
            # Format hour for display
            hour = int(item_details.get('checkout_hour', 8))
            hour_display = f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}"
            
            cart_items.append({
                'board': board,
                'location': location,
                'checkout_date': item_details.get('checkout_date'),
                'checkout_hour': item_details.get('checkout_hour'),
                'checkout_hour_display': hour_display,
                'duration_hours': item_details.get('duration_hours'),
                'timezone': location.timezone if location else 'America/New_York'
            })
            valid_cart.append(item_details)
    
    # Update cart if some items were removed
    if len(valid_cart) != len(cart):
        save_cart(valid_cart)
        if len(valid_cart) < len(cart):
            flash('Some boards were removed from your cart (no longer available)', 'warning')
    
    return render_template('user/cart.html', cart_items=cart_items)


@cart_routes.route('/cart/add/<board_id>', methods=['POST'])
@login_required
def add_to_cart(board_id):
    """Add board to cart with checkout details"""
    location_id = get_selected_location_id()
    
    if not location_id:
        return jsonify({'success': False, 'error': 'No location selected'}), 400
    
    # Get checkout details from session (set on dashboard)
    # Dashboard saves as checkout_date, checkout_hour, checkout_duration
    checkout_date = session.get('checkout_date')
    checkout_hour = session.get('checkout_hour', '8')
    duration_hours = session.get('checkout_duration', '1')
    
    if not checkout_date:
        return jsonify({'success': False, 'error': 'Please select a checkout date on the dashboard first'}), 400
    
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
    
    # Parse selected checkout date
    from models.reservation import Reservation
    
    selected_checkout_date = None
    if checkout_date:
        try:
            selected_checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Check if board is already in cart
    cart = get_cart()
    for item in cart:
        item_board_id = item.get('board_id') if isinstance(item, dict) else item
        if item_board_id == board_id:
            return jsonify({'success': False, 'error': 'Board is already in your cart'}), 400
    
    # Check for date conflicts with existing scheduled checkouts from different locations
    active_checkouts = Checkout.find_active_by_user(current_user.id)
    for checkout in active_checkouts:
        checkout_board = Board.find_by_id(checkout.board_id)
        if checkout_board and checkout_board.location_id != board.location_id:
            checkout_date_obj = checkout.checkout_time.date() if checkout.checkout_time else None
            if selected_checkout_date and checkout_date_obj and selected_checkout_date == checkout_date_obj:
                checkout_location = Location.find_by_id(checkout_board.location_id)
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
                reservation_date = reservation.unlock_time.date() if reservation.unlock_time else None
                if selected_checkout_date and reservation_date and selected_checkout_date == reservation_date:
                    reservation_location = Location.find_by_id(reservation_board.location_id)
                    return jsonify({
                        'success': False,
                        'error': f'You already have a reservation at {reservation_location.name if reservation_location else "another location"} on {selected_checkout_date.strftime("%b %d, %Y")}. You cannot reserve boards from different locations on the same day.'
                    }), 400
    
    # Check for date conflicts with items already in cart from different locations
    for item in cart:
        if isinstance(item, dict):
            item_location_id = item.get('location_id')
            item_date = item.get('checkout_date')
            if item_location_id and item_location_id != location_id:
                if item_date and checkout_date and item_date == checkout_date:
                    item_location = Location.find_by_id(item_location_id)
                    return jsonify({
                        'success': False,
                        'error': f'You have a board in your cart from {item_location.name if item_location else "another location"} on this same date. Different locations must be on different days.'
                    }), 400
    
    # Create cart item with all checkout details
    cart_item = {
        'board_id': board_id,
        'location_id': location_id,
        'checkout_date': checkout_date,
        'checkout_hour': checkout_hour,
        'duration_hours': duration_hours
    }
    
    cart.append(cart_item)
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
    new_cart = []
    
    for item in cart:
        item_board_id = item.get('board_id') if isinstance(item, dict) else item
        if item_board_id != board_id:
            new_cart.append(item)
    
    save_cart(new_cart)
    
    return jsonify({
        'success': True,
        'message': 'Board removed from cart',
        'cart_count': len(new_cart)
    })


@cart_routes.route('/cart/checkout', methods=['POST'])
@login_required
def checkout_cart():
    """Checkout all items in cart - each item has its own date/time/location"""
    cart = get_cart()
    
    if not cart:
        return jsonify({'success': False, 'error': 'Cart is empty'}), 400
    
    checkouts = []
    errors = []
    
    try:
        for item in cart:
            # Handle both old format (string) and new format (dict)
            if isinstance(item, str):
                # Old format - skip, shouldn't happen with new code
                errors.append(f"Invalid cart item format")
                continue
            
            board_id = item.get('board_id')
            location_id = item.get('location_id')
            checkout_date = item.get('checkout_date')
            checkout_hour = item.get('checkout_hour', '8')
            duration_hours = int(item.get('duration_hours', 1))
            
            if not all([board_id, location_id, checkout_date]):
                errors.append(f"Missing checkout details for a board")
                continue
            
            try:
                # Verify board is still available
                board = Board.find_by_id(board_id)
                if not board:
                    errors.append(f"Board not found")
                    continue
                
                if not board.is_available():
                    errors.append(f"Board {board.name} is no longer available")
                    continue
                
                # Check for active checkout
                active_checkout = Checkout.find_active_by_board(board_id)
                if active_checkout:
                    errors.append(f"Board {board.name} is already checked out")
                    continue
                
                # Parse datetime
                hour = int(checkout_hour)
                checkout_datetime_str = f"{checkout_date} {hour:02d}:00"
                checkout_datetime_local = datetime.strptime(checkout_datetime_str, '%Y-%m-%d %H:%M')
                
                # Convert to UTC for storage
                tz = timezone_service.get_location_timezone(location_id)
                checkout_datetime_local = tz.localize(checkout_datetime_local)
                checkout_datetime_utc = checkout_datetime_local.astimezone(pytz.UTC)
                
                # Calculate return time
                if duration_hours < 1:
                    duration_hours = 1
                elif duration_hours > 24:
                    duration_hours = 24
                
                expected_return_time = checkout_datetime_utc + timedelta(hours=duration_hours)
                
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
                    is_weekend = checkout_datetime_local.weekday() >= 5
                    log = ActivityLog(
                        user_id=current_user.id,
                        board_id=board_id,
                        action_type=ActivityLog.ACTION_CHECKOUT,
                        action_details={
                            'checkout_id': checkout.id,
                            'expected_return_time': expected_return_time.isoformat(),
                            'is_weekend': is_weekend,
                            'location_id': location_id,
                            'duration_hours': duration_hours
                        },
                        location_id=location_id,
                        ip_address=request.remote_addr
                    )
                    db.session.add(log)
                except Exception as log_error:
                    logger.error(f"Error creating activity log: {log_error}")
                
                checkouts.append(checkout)
                
            except Exception as e:
                logger.error(f"Error checking out board {board_id}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                errors.append(f"Error checking out board: {str(e)}")
        
        # Commit all checkouts at once
        if checkouts:
            db.session.commit()
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


@cart_routes.route('/api/cart-items', methods=['GET'])
@login_required
def get_cart_items():
    """API endpoint to get current cart items (for updating dashboard buttons)"""
    cart = get_cart()
    cart_item_ids = []
    
    for item in cart:
        if isinstance(item, dict):
            cart_item_ids.append({'id': item.get('board_id')})
        else:
            cart_item_ids.append({'id': item})
    
    return jsonify({
        'success': True,
        'cart_items': cart_item_ids
    })
