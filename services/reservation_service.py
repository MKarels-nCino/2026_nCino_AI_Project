"""Reservation service - Handles board reservations"""
from datetime import datetime
from models.reservation import Reservation
from models.checkout import Checkout
from models.board import Board
from models.activity_log import ActivityLog
from services.timezone_service import TimezoneService
from utils.constants import (
    ERROR_CHECKOUT_NOT_FOUND, ERROR_RESERVATION_EXISTS, ERROR_RETURN_TIME_PASSED,
    ERROR_RESERVATION_NOT_FOUND, ERROR_RESERVATION_NOT_BELONGS, ERROR_RESERVATION_NOT_AVAILABLE,
    ERROR_RESERVATION_CANNOT_CANCEL
)
import logging

logger = logging.getLogger(__name__)


class ReservationService:
    """Service for handling board reservations"""
    
    def __init__(self, timezone_service=None):
        self.timezone_service = timezone_service or TimezoneService()
    
    def create_reservation(self, user_id, board_id, checkout_id, location_id, ip_address=None):
        """
        Create a reservation for a board after a checkout's return time
        Returns: Reservation object
        Raises: Exception if reservation cannot be created
        """
        # Get checkout to find return time
        checkout = Checkout.find_by_id(checkout_id)
        if not checkout:
            raise Exception(ERROR_CHECKOUT_NOT_FOUND)
        
        if checkout.board_id != board_id:
            raise Exception("Checkout does not match board")
        
        if not checkout.is_active():
            raise Exception("Checkout is not active")
        
        # Calculate unlock time (expected return time in location timezone)
        unlock_time = self.timezone_service.to_location_timezone(
            checkout.expected_return_time, location_id
        )
        
        # Verify unlock time hasn't passed
        if self.timezone_service.is_unlock_time_passed(checkout.expected_return_time, location_id):
            raise Exception(ERROR_RETURN_TIME_PASSED)
        
        # Check if user already has a reservation for this checkout
        existing = Reservation.find_by_user(user_id)
        for res in existing:
            if res.checkout_id == checkout_id and res.is_pending():
                raise Exception(ERROR_RESERVATION_EXISTS)
        
        # Create reservation
        reservation = Reservation(
            user_id=user_id,
            board_id=board_id,
            checkout_id=checkout_id,
            reservation_time=datetime.utcnow(),
            unlock_time=checkout.expected_return_time,  # Store in UTC
            status=Reservation.STATUS_PENDING
        )
        reservation.save()
        
        # Log activity
        ActivityLog.create_log(
            user_id=user_id,
            board_id=board_id,
            action_type=ActivityLog.ACTION_RESERVATION,
            action_details={
                'reservation_id': reservation.id,
                'checkout_id': checkout_id,
                'unlock_time': checkout.expected_return_time.isoformat()
            },
            location_id=location_id,
            ip_address=ip_address
        )
        
        logger.info(f"Reservation created: {reservation.id} for board {board_id}")
        return reservation
    
    def get_reservation_queue(self, board_id):
        """Get reservation queue for a board"""
        return Reservation.find_pending_by_board(board_id)
    
    def check_available_reservations(self, board_id):
        """
        Check if any reservations are now available (unlock time passed)
        Returns: List of available reservations
        """
        board = Board.find_by_id(board_id)
        if not board:
            return []
        
        available_reservations = Reservation.find_available(board_id)
        return available_reservations
    
    def fulfill_reservation(self, reservation_id, user_id, location_id, ip_address=None):
        """
        Fulfill a reservation (user checks out the board)
        Returns: Checkout object
        """
        reservation = Reservation.find_by_id(reservation_id)
        if not reservation:
            raise Exception(ERROR_RESERVATION_NOT_FOUND)
        
        if reservation.user_id != user_id:
            raise Exception(ERROR_RESERVATION_NOT_BELONGS)
        
        if reservation.status != Reservation.STATUS_AVAILABLE:
            raise Exception(ERROR_RESERVATION_NOT_AVAILABLE)
        
        # Mark reservation as fulfilled
        reservation.mark_fulfilled()
        
        # Log activity
        ActivityLog.create_log(
            user_id=user_id,
            board_id=reservation.board_id,
            action_type=ActivityLog.ACTION_RESERVATION,
            action_details={
                'reservation_id': reservation_id,
                'action': 'fulfilled'
            },
            location_id=location_id,
            ip_address=ip_address
        )
        
        logger.info(f"Reservation {reservation_id} fulfilled by user {user_id}")
        return reservation
    
    def cancel_reservation(self, reservation_id, user_id, location_id, ip_address=None):
        """Cancel a reservation"""
        reservation = Reservation.find_by_id(reservation_id)
        if not reservation:
            raise Exception(ERROR_RESERVATION_NOT_FOUND)
        
        if reservation.user_id != user_id:
            raise Exception(ERROR_RESERVATION_NOT_BELONGS)
        
        if not reservation.is_pending():
            raise Exception(ERROR_RESERVATION_CANNOT_CANCEL)
        
        reservation.cancel()
        
        # Log activity
        ActivityLog.create_log(
            user_id=user_id,
            board_id=reservation.board_id,
            action_type=ActivityLog.ACTION_CANCEL_RESERVATION,
            action_details={'reservation_id': reservation_id},
            location_id=location_id,
            ip_address=ip_address
        )
        
        logger.info(f"Reservation {reservation_id} cancelled by user {user_id}")
        return reservation
    
    def get_pending_notifications(self):
        """Get reservations that need notifications sent"""
        return Reservation.find_pending_notifications()
