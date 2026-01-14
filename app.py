from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_socketio import SocketIO
from config import Config
from database import db

# Import models so SQLAlchemy can create tables
from models import (
    Location,
    User,
    Board,
    Checkout,
    Reservation,
    ActivityLog,
    DamageReport,
    BoardRating,
)
from routes.auth_routes import auth_routes
from routes.user_routes import user_routes
from routes.admin_routes import admin_routes
from routes.api_routes import api_routes
from routes.cart_routes import cart_routes
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize extensions
login_manager = LoginManager()
socketio = SocketIO(cors_allowed_origins="*")


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.find_by_id(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    """Handle unauthorized access"""
    return redirect(url_for("auth_routes.login"))


def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure SQLite database (following Flask-SQLAlchemy docs)
    import os

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"sqlite:///{os.path.join(basedir, 'surfboard_checkout.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth_routes.login"
    login_manager.login_message = "Please log in to access this page."
    socketio.init_app(
        app, cors_allowed_origins=app.config.get("SOCKETIO_CORS_ALLOWED_ORIGINS", "*")
    )
    # Store socketio in app extensions for access from routes
    app.extensions["socketio"] = socketio

    # Create all tables (must be after db.init_app and model imports)
    with app.app_context():
        db.create_all()
        logger.info("✓ Database initialized (SQLite)")

    # Register blueprints
    app.register_blueprint(auth_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(admin_routes)
    app.register_blueprint(api_routes)
    app.register_blueprint(cart_routes)

    @app.route("/")
    def index():
        """Home page - redirect to dashboard or login"""
        return redirect(url_for("user_routes.dashboard"))

    @app.route("/health")
    def health():
        """Health check endpoint"""
        return {"status": "healthy", "message": "Application is running"}

    @app.route("/db/test")
    def test_db():
        """Test database connection endpoint"""
        try:
            from sqlalchemy import select, text

            result = db.session.execute(text("SELECT 1")).scalar()
            return {
                "status": "success",
                "message": "Database connection successful",
                "database": "SQLite",
            }, 200
        except Exception as e:
            return {
                "status": "error",
                "message": "Database connection failed",
                "error": str(e),
            }, 500

    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors"""
        return {"error": "Not found"}, 404

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors"""
        logger.error(f"Internal error: {error}")
        return {"error": "Internal server error"}, 500

    @app.teardown_appcontext
    def close_db(error):
        """Close database connections when app context tears down"""
        pass

    return app


# SocketIO event handlers
@socketio.on("connect")
def handle_connect():
    """Handle WebSocket connection"""
    logger.info("Client connected")
    from flask_socketio import emit

    emit("connected", {"message": "Connected to server"})


@socketio.on("disconnect")
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info("Client disconnected")


@socketio.on("subscribe_location")
def handle_subscribe_location(data):
    """Handle location subscription for real-time updates"""
    from flask_socketio import join_room

    location_id = data.get("location_id")
    logger.info(f"Client subscribed to location: {location_id}")
    # Join room for location-specific updates
    join_room(f"location_{location_id}")


if __name__ == "__main__":
    app = create_app()
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
