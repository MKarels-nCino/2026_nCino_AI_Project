"""Checkout service - Handles board checkout and return logic"""
from datetime import datetime
from models.board import Board
from models.checkout import Checkout
from models.damage_report import DamageReport
from models.activity_log import ActivityLog
from services.timezone_service import TimezoneService
from utils.constants import (
    ERROR_BOARD_NOT_FOUND, ERROR_BOARD_NOT_AVAILABLE, ERROR_BOARD_ALREADY_CHECKED_OUT,
    ERROR_BOARD_NOT_AT_LOCATION, ERROR_CHECKOUT_NOT_FOUND, ERROR_CHECKOUT_NOT_ACTIVE,
    ERROR_CHECKOUT_NOT_BELONGS, DAMAGE_SEVERITY_MODERATE
)
import logging

logger = logging.getLogger(__name__)


class CheckoutService:
    """Service for handling board checkouts and returns"""
    
    def __init__(self, timezone_service=None):
        self.timezone_service = timezone_service or TimezoneService()
    
    def checkout_board(self, user_id, board_id, location_id, ip_address=None):
        """
        Checkout a board for a user
        Returns: Checkout object
        Raises: Exception if board not available
        """
        # Get board and verify availability
        board = Board.find_by_id(board_id)
        if not board:
            raise Exception(ERROR_BOARD_NOT_FOUND)
        
        if board.location_id != location_id:
            raise Exception(ERROR_BOARD_NOT_AT_LOCATION)
        
        if not board.is_available():
            raise Exception(ERROR_BOARD_NOT_AVAILABLE)
        
        # Check for active checkout (concurrent operation protection)
        active_checkout = Checkout.find_active_by_board(board_id)
        if active_checkout:
            raise Exception(ERROR_BOARD_ALREADY_CHECKED_OUT)
        
        # Create checkout
        checkout_time = datetime.utcnow()
        expected_return_time, is_weekend = self.timezone_service.calculate_return_window(
            checkout_time, location_id
        )
        
        checkout = Checkout(
            user_id=user_id,
            board_id=board_id,
            checkout_time=checkout_time,
            expected_return_time=expected_return_time,
            status=Checkout.STATUS_ACTIVE
        )
        checkout.save()
        
        # Update board status
        board.update_status(Board.STATUS_CHECKED_OUT)
        
        # Log activity
        ActivityLog.create_log(
            user_id=user_id,
            board_id=board_id,
            action_type=ActivityLog.ACTION_CHECKOUT,
            action_details={
                'checkout_id': checkout.id,
                'expected_return_time': expected_return_time.isoformat(),
                'is_weekend': is_weekend
            },
            location_id=location_id,
            ip_address=ip_address
        )
        
        logger.info(f"Board {board_id} checked out by user {user_id}")
        return checkout
    
    def return_board(self, checkout_id, user_id, location_id, damage_report=None, ip_address=None):
        """
        Return a board
        Returns: Checkout object
        Raises: Exception if checkout not found or not active
        """
        checkout = Checkout.find_by_id(checkout_id)
        if not checkout:
            raise Exception(ERROR_CHECKOUT_NOT_FOUND)
        
        if checkout.user_id != user_id:
            raise Exception(ERROR_CHECKOUT_NOT_BELONGS)
        
        if not checkout.is_active():
            raise Exception(ERROR_CHECKOUT_NOT_ACTIVE)
        
        # Mark checkout as returned
        return_time = datetime.utcnow()
        checkout.mark_returned(return_time)
        
        # Get board
        board = Board.find_by_id(checkout.board_id)
        
        # Handle damage report if provided
        if damage_report:
            damage = DamageReport(
                checkout_id=checkout_id,
                board_id=checkout.board_id,
                reported_by=user_id,
                description=damage_report.get('description', ''),
                severity=damage_report.get('severity', DAMAGE_SEVERITY_MODERATE)
            )
            damage.save()
            
            # Update board status to damaged
            board.update_status(Board.STATUS_DAMAGED)
            
            # Notify admins about damage
            from services.notification_service import NotificationService
            notification_service = NotificationService()
            notification_service.notify_damage_reported(damage, location_id)
            
            # Log damage report
            ActivityLog.create_log(
                user_id=user_id,
                board_id=checkout.board_id,
                action_type=ActivityLog.ACTION_DAMAGE_REPORT,
                action_details={
                    'checkout_id': checkout_id,
                    'damage_report_id': damage.id,
                    'severity': damage.severity
                },
                location_id=location_id,
                ip_address=ip_address
            )
        else:
            # Board is available again
            board.update_status(Board.STATUS_AVAILABLE)
            
            # Check for pending reservations and send notifications
            from services.reservation_service import ReservationService
            from services.notification_service import NotificationService
            reservation_service = ReservationService()
            notification_service = NotificationService()
            
            # Check if any reservations are now available
            available_reservations = reservation_service.check_available_reservations(checkout.board_id)
            for reservation in available_reservations:
                reservation.mark_available()
                # Send notification
                notification_service.notify_reservation_available(reservation)
                # Also send WebSocket notification
                try:
                    from flask import current_app
                    socketio = current_app.extensions.get('socketio')
                    if socketio:
                        socketio.emit('notification', {
                            'user_id': reservation.user_id,
                            'message': f'Your reserved board "{board.name}" is now available!',
                            'type': 'success'
                        }, room=f'location_{location_id}')
                except Exception as e:
                    logger.error(f"Error sending WebSocket notification: {e}")
        
        # Log return activity
        ActivityLog.create_log(
            user_id=user_id,
            board_id=checkout.board_id,
            action_type=ActivityLog.ACTION_RETURN,
            action_details={
                'checkout_id': checkout_id,
                'return_time': return_time.isoformat(),
                'has_damage': damage_report is not None
            },
            location_id=location_id,
            ip_address=ip_address
        )
        
        logger.info(f"Board {checkout.board_id} returned by user {user_id}")
        return checkout
    
    def cancel_checkout(self, checkout_id, user_id, location_id, ip_address=None):
        """
        Cancel an active checkout
        Returns: Checkout object
        """
        checkout = Checkout.find_by_id(checkout_id)
        if not checkout:
            raise Exception(ERROR_CHECKOUT_NOT_FOUND)
        
        if checkout.user_id != user_id:
            raise Exception(ERROR_CHECKOUT_NOT_BELONGS)
        
        if not checkout.is_active():
            raise Exception(ERROR_CHECKOUT_NOT_ACTIVE)
        
        # Cancel checkout
        checkout.cancel()
        
        # Update board status back to available
        board = Board.find_by_id(checkout.board_id)
        board.update_status(Board.STATUS_AVAILABLE)
        
        # Log activity
        ActivityLog.create_log(
            user_id=user_id,
            board_id=checkout.board_id,
            action_type=ActivityLog.ACTION_CANCEL_CHECKOUT,
            action_details={'checkout_id': checkout_id},
            location_id=location_id,
            ip_address=ip_address
        )
        
        logger.info(f"Checkout {checkout_id} cancelled by user {user_id}")
        return checkout
