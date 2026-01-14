"""Admin portal routes"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from utils.decorators import admin_required, require_location_access
from models.board import Board
from models.checkout import Checkout
from models.damage_report import DamageReport
from models.activity_log import ActivityLog
from models.location import Location
from services.reporting_service import ReportingService
from services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)

admin_routes = Blueprint('admin_routes', __name__, url_prefix='/admin')
reporting_service = ReportingService()
notification_service = NotificationService()


@admin_routes.route('/dashboard')
@login_required
@admin_required
@require_location_access
def dashboard():
    """Admin dashboard"""
    location_id = current_user.location_id
    
    # Get stats
    available_boards = Board.find_available(location_id)
    checked_out_boards = Board.find_by_status(location_id, Board.STATUS_CHECKED_OUT)
    damaged_boards = Board.find_by_status(location_id, Board.STATUS_DAMAGED)
    
    # Get recent checkouts
    recent_checkouts = Checkout.find_by_location(location_id, limit=10)
    # Get user info for checkouts
    from models.user import User
    for checkout in recent_checkouts:
        user = User.find_by_id(checkout.user_id)
        checkout.user = user
    
    # Get new damage reports
    new_damage = DamageReport.find_by_location(location_id, DamageReport.STATUS_NEW)
    
    return render_template('admin/dashboard.html',
                         available_count=len(available_boards),
                         checked_out_count=len(checked_out_boards),
                         damaged_count=len(damaged_boards),
                         recent_checkouts=recent_checkouts,
                         new_damage=new_damage)


@admin_routes.route('/inventory')
@login_required
@admin_required
@require_location_access
def inventory():
    """View all boards"""
    boards_list = Board.find_by_location(current_user.location_id)
    return render_template('admin/inventory.html', boards=boards_list)


@admin_routes.route('/checkout-schedule')
@login_required
@admin_required
@require_location_access
def checkout_schedule():
    """Checkout schedule/calendar view"""
    from datetime import datetime
    # Get all checkouts at location
    checkouts = Checkout.find_by_location(current_user.location_id)
    # Get board and user info for each checkout
    from models.user import User
    for checkout in checkouts:
        board = Board.find_by_id(checkout.board_id)
        user = User.find_by_id(checkout.user_id)
        checkout.board = board
        checkout.user = user
    
    # Get all boards for filter
    boards = Board.find_by_location(current_user.location_id)
    
    return render_template('admin/checkout_schedule.html',
                         checkouts=checkouts,
                         boards=boards,
                         today=datetime.now().strftime('%Y-%m-%d'),
                         now=datetime.now())


@admin_routes.route('/damage-queue')
@login_required
@admin_required
@require_location_access
def damage_queue():
    """Damage queue management"""
    damage_reports = DamageReport.find_by_location(current_user.location_id)
    return render_template('admin/damage_queue.html', damage_reports=damage_reports)


@admin_routes.route('/activity-log')
@login_required
@admin_required
@require_location_access
def activity_log():
    """Activity log"""
    activities = ActivityLog.find_by_location(current_user.location_id, limit=100)
    return render_template('admin/activity_log.html', activities=activities)


@admin_routes.route('/reports')
@login_required
@admin_required
@require_location_access
def reports():
    """Reports and analytics"""
    location_id = current_user.location_id
    
    favorite_boards = reporting_service.get_favorite_boards(location_id)
    usage_per_user = reporting_service.get_usage_per_user(location_id)
    usage_trends = reporting_service.get_usage_trends(location_id)
    seasonal_trends = reporting_service.get_seasonal_trends(location_id)
    peak_times = reporting_service.get_peak_usage_times(location_id)
    damage_frequency = reporting_service.get_damage_frequency_by_board(location_id)
    ratings_summary = reporting_service.get_board_ratings_summary(location_id)
    
    # Convert usage_trends to JSON-serializable format
    usage_trends_json = [{'date': str(trend['date']), 'checkout_count': trend['checkout_count']} for trend in usage_trends]
    
    return render_template('admin/reports.html',
                         favorite_boards=favorite_boards,
                         usage_per_user=usage_per_user,
                         usage_trends=usage_trends_json,
                         seasonal_trends=seasonal_trends,
                         peak_times=peak_times,
                         damage_frequency=damage_frequency,
                         ratings_summary=ratings_summary)


@admin_routes.route('/api/damage/<report_id>/update-status', methods=['POST'])
@login_required
@admin_required
@require_location_access
def update_damage_status(report_id):
    """API endpoint to update damage report status"""
    try:
        damage = DamageReport.find_by_id(report_id)
        if not damage:
            return jsonify({'success': False, 'error': 'Damage report not found'}), 404
        
        new_status = request.json.get('status')
        admin_notes = request.json.get('admin_notes')
        
        damage.update_status(new_status, admin_notes)
        
        # If status is 'replaced', update board status
        if new_status == DamageReport.STATUS_REPLACED:
            board = Board.find_by_id(damage.board_id)
            board.update_status(Board.STATUS_AVAILABLE)
        
        return jsonify({
            'success': True,
            'damage_report': damage.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Update damage status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400
