"""API routes for AJAX calls"""

from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from flask_socketio import emit
from models.board import Board
from models.checkout import Checkout
from models.reservation import Reservation
from models.location import Location
from services.checkout_service import CheckoutService
from services.reservation_service import ReservationService
from services.timezone_service import TimezoneService
from utils.constants import (
    MSG_CHECKOUT_SUCCESS,
    MSG_CHECKOUT_FAILED,
    MSG_RETURN_SUCCESS,
    MSG_RETURN_FAILED,
    MSG_CANCEL_SUCCESS,
    MSG_CANCEL_FAILED,
    MSG_RESERVATION_SUCCESS,
    MSG_RESERVATION_FAILED,
    BOARD_STATUS_CHECKED_OUT,
    BOARD_STATUS_DAMAGED,
    BOARD_STATUS_AVAILABLE,
)
import logging

logger = logging.getLogger(__name__)

api_routes = Blueprint("api_routes", __name__, url_prefix="/api")
checkout_service = CheckoutService()
reservation_service = ReservationService()
timezone_service = TimezoneService()


def get_selected_location_id():
    """Get the currently selected location ID from session, or default to user's location"""
    location_id = session.get("selected_location_id")
    if not location_id and current_user.is_authenticated:
        location_id = current_user.location_id
        if not location_id:
            first_location = Location.find_all()
            if first_location:
                location_id = first_location[0].id
        # Always save to session so it persists
        if location_id:
            session["selected_location_id"] = location_id
            session.permanent = True  # Make session persist
    return location_id


@api_routes.route("/checkout/<board_id>", methods=["POST"])
@login_required
def checkout_board(board_id):
    """API endpoint to checkout a board"""
    try:
        location_id = get_selected_location_id()
        if not location_id:
            return jsonify({"success": False, "error": "No location selected"}), 400

        # Verify board belongs to selected location
        board = Board.find_by_id(board_id)
        if not board or board.location_id != location_id:
            return (
                jsonify(
                    {"success": False, "error": "Board not found at selected location"}
                ),
                404,
            )

        ip_address = request.remote_addr
        checkout = checkout_service.checkout_board(
            current_user.id, board_id, location_id, ip_address
        )

        # Emit real-time update
        try:
            from flask import current_app

            socketio = current_app.extensions.get("socketio")
            if socketio:
                socketio.emit(
                    "board_status_changed",
                    {
                        "board_id": board_id,
                        "status": BOARD_STATUS_CHECKED_OUT,
                        "location_id": location_id,
                    },
                    room=f"location_{location_id}",
                )
                socketio.emit(
                    "checkout_created",
                    {
                        "checkout_id": checkout.id,
                        "board_id": board_id,
                        "user_id": current_user.id,
                        "location_id": location_id,
                    },
                    room=f"location_{location_id}",
                )
        except Exception as e:
            logger.error(f"Error emitting socket event: {e}")

        return jsonify({"success": True, "checkout": checkout.to_dict()}), 200
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@api_routes.route("/return/<checkout_id>", methods=["POST"])
@login_required
def return_board(checkout_id):
    """API endpoint to return a board"""
    try:
        location_id = get_selected_location_id()
        if not location_id:
            return jsonify({"success": False, "error": "No location selected"}), 400

        damage_report = None
        if request.json and request.json.get("has_damage"):
            damage_report = {
                "description": request.json.get("damage_description", ""),
                "severity": request.json.get("severity", "moderate"),
            }

        ip_address = request.remote_addr
        checkout = checkout_service.return_board(
            checkout_id, current_user.id, location_id, damage_report, ip_address
        )
        
        # Handle rating if provided
        if request.json and request.json.get("rating"):
            from models.board_rating import BoardRating
            rating = BoardRating(
                board_id=checkout.board_id,
                user_id=current_user.id,
                checkout_id=checkout_id,
                rating=int(request.json.get("rating")),
                review=request.json.get("review")
            )
            rating.save()

        # Emit real-time update
        try:
            from flask import current_app

            socketio = current_app.extensions.get("socketio")
            if socketio:
                board_status = (
                    BOARD_STATUS_DAMAGED if damage_report else BOARD_STATUS_AVAILABLE
                )
                socketio.emit(
                    "board_status_changed",
                    {
                        "board_id": checkout.board_id,
                        "status": board_status,
                        "location_id": location_id,
                    },
                    room=f"location_{location_id}",
                )
                socketio.emit(
                    "checkout_returned",
                    {
                        "checkout_id": checkout.id,
                        "board_id": checkout.board_id,
                        "location_id": location_id,
                    },
                    room=f"location_{location_id}",
                )
        except Exception as e:
            logger.error(f"Error emitting socket event: {e}")

        return jsonify({"success": True, "checkout": checkout.to_dict()}), 200
    except Exception as e:
        logger.error(f"Return error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@api_routes.route("/cancel-checkout/<checkout_id>", methods=["POST"])
@login_required
def cancel_checkout(checkout_id):
    """API endpoint to cancel a checkout"""
    try:
        location_id = get_selected_location_id()
        if not location_id:
            return jsonify({"success": False, "error": "No location selected"}), 400

        ip_address = request.remote_addr
        checkout = checkout_service.cancel_checkout(
            checkout_id, current_user.id, location_id, ip_address
        )
        return jsonify({"success": True, "checkout": checkout.to_dict()}), 200
    except Exception as e:
        logger.error(f"Cancel checkout error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@api_routes.route("/reserve/<board_id>/<checkout_id>", methods=["POST"])
@login_required
def create_reservation(board_id, checkout_id):
    """API endpoint to create a reservation"""
    try:
        location_id = get_selected_location_id()
        if not location_id:
            return jsonify({"success": False, "error": "No location selected"}), 400

        ip_address = request.remote_addr
        reservation = reservation_service.create_reservation(
            current_user.id, board_id, checkout_id, location_id, ip_address
        )
        return jsonify({"success": True, "reservation": reservation.to_dict()}), 200
    except Exception as e:
        logger.error(f"Reservation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@api_routes.route("/fulfill-reservation/<reservation_id>", methods=["POST"])
@login_required
def fulfill_reservation(reservation_id):
    """API endpoint to fulfill a reservation"""
    try:
        location_id = get_selected_location_id()
        if not location_id:
            return jsonify({"success": False, "error": "No location selected"}), 400

        ip_address = request.remote_addr
        reservation = reservation_service.fulfill_reservation(
            reservation_id, current_user.id, location_id, ip_address
        )
        return jsonify({"success": True, "reservation": reservation.to_dict()}), 200
    except Exception as e:
        logger.error(f"Fulfill reservation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@api_routes.route("/cancel-reservation/<reservation_id>", methods=["POST"])
@login_required
def cancel_reservation(reservation_id):
    """API endpoint to cancel a reservation"""
    try:
        location_id = get_selected_location_id()
        if not location_id:
            return jsonify({"success": False, "error": "No location selected"}), 400

        ip_address = request.remote_addr
        reservation = reservation_service.cancel_reservation(
            reservation_id, current_user.id, location_id, ip_address
        )
        return jsonify({"success": True, "reservation": reservation.to_dict()}), 200
    except Exception as e:
        logger.error(f"Cancel reservation error: {e}")
        return jsonify({"success": False, "error": str(e)}), 400


@api_routes.route("/boards/available", methods=["GET"])
@login_required
def get_available_boards():
    """API endpoint to get available boards"""
    location_id = get_selected_location_id()
    if not location_id:
        return jsonify({"success": False, "error": "No location selected"}), 400

    boards_list = Board.find_available(location_id)
    return (
        jsonify(
            {"success": True, "boards": [board.to_dict() for board in boards_list]}
        ),
        200,
    )


@api_routes.route("/reservations/queue/<board_id>", methods=["GET"])
@login_required
def get_reservation_queue(board_id):
    """API endpoint to get reservation queue for a board"""
    queue = reservation_service.get_reservation_queue(board_id)
    return jsonify({"success": True, "queue": [r.to_dict() for r in queue]}), 200
