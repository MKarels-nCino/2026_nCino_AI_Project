"""Notification service - Handles email and in-app notifications"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config
from models.user import User
from models.board import Board
from models.reservation import Reservation
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications (email and in-app)"""
    
    def __init__(self):
        self.config = Config()
        self.email_enabled = bool(self.config.MAIL_USERNAME and self.config.MAIL_PASSWORD)
    
    def send_email(self, to_email, subject, body_html, body_text=None):
        """Send an email notification"""
        if not self.email_enabled:
            logger.warning(f"Email not configured. Would send to {to_email}: {subject}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.config.MAIL_DEFAULT_SENDER
            msg['To'] = to_email
            
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))
            
            with smtplib.SMTP(self.config.MAIL_SERVER, self.config.MAIL_PORT) as server:
                if self.config.MAIL_USE_TLS:
                    server.starttls()
                server.login(self.config.MAIL_USERNAME, self.config.MAIL_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def notify_reservation_available(self, reservation):
        """
        Notify user that their reserved board is now available
        """
        user = User.find_by_id(reservation.user_id)
        board = Board.find_by_id(reservation.board_id)
        
        if not user or not board:
            return False
        
        subject = f"Your reserved surfboard '{board.name}' is now available!"
        
        body_html = f"""
        <html>
        <body>
            <h2>Your Reserved Board is Available!</h2>
            <p>Hi {user.full_name},</p>
            <p>Great news! The surfboard you reserved is now available for checkout:</p>
            <ul>
                <li><strong>Board:</strong> {board.name}</li>
                <li><strong>Brand:</strong> {board.brand or 'N/A'}</li>
                <li><strong>Size:</strong> {board.size or 'N/A'}</li>
            </ul>
            <p>You can now check out this board from your dashboard.</p>
            <p>This reservation will remain available for you to claim.</p>
        </body>
        </html>
        """
        
        body_text = f"""
        Your Reserved Board is Available!
        
        Hi {user.full_name},
        
        Great news! The surfboard you reserved is now available for checkout:
        
        Board: {board.name}
        Brand: {board.brand or 'N/A'}
        Size: {board.size or 'N/A'}
        
        You can now check out this board from your dashboard.
        """
        
        success = self.send_email(user.email, subject, body_html, body_text)
        
        if success:
            reservation.mark_notification_sent()
        
        return success
    
    def notify_damage_reported(self, damage_report, location_id):
        """
        Notify admins when a board is reported as damaged
        """
        from models.damage_report import DamageReport
        from models.location import Location
        
        board = Board.find_by_id(damage_report.board_id)
        location = Location.find_by_id(location_id)
        admins = User.find_admins_by_location(location_id)
        
        if not board or not admins:
            return False
        
        subject = f"Damage Reported: {board.name} at {location.name}"
        
        body_html = f"""
        <html>
        <body>
            <h2>Board Damage Reported</h2>
            <p>A board has been reported as damaged:</p>
            <ul>
                <li><strong>Board:</strong> {board.name}</li>
                <li><strong>Location:</strong> {location.name}</li>
                <li><strong>Severity:</strong> {damage_report.severity}</li>
                <li><strong>Description:</strong> {damage_report.description}</li>
            </ul>
            <p>Please review the damage queue in the admin portal.</p>
        </body>
        </html>
        """
        
        body_text = f"""
        Board Damage Reported
        
        A board has been reported as damaged:
        
        Board: {board.name}
        Location: {location.name}
        Severity: {damage_report.severity}
        Description: {damage_report.description}
        
        Please review the damage queue in the admin portal.
        """
        
        success_count = 0
        for admin in admins:
            if self.send_email(admin.email, subject, body_html, body_text):
                success_count += 1
        
        return success_count > 0
    
    def send_in_app_notification(self, user_id, message, notification_type='info'):
        """
        Send in-app notification (via WebSocket)
        This will be handled by the WebSocket handler
        Returns notification data structure
        """
        return {
            'user_id': user_id,
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat()
        }
