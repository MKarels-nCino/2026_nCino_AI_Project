import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database connection - support both DATABASE_URL and individual parameters
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Database connection parameters (legacy - not used with SQLite)
    # Kept for backwards compatibility if needed
    DB_USER = os.environ.get('user') or os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('password') or os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('host') or os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('port') or os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('dbname') or os.environ.get('DB_NAME')
    
    # Email configuration (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    
    # Application settings
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('SOCKETIO_CORS_ALLOWED_ORIGINS', '*').split(',')
    
    def get_database_url(self, use_pooling=False):
        """Get database URL, either from DATABASE_URL or build from individual parameters
        
        Args:
            use_pooling: If True and port is 5432, change to 6543 for connection pooling
        """
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            # Default to connection pooling (port 6543) - doesn't require IP allowlist
            if ':5432/' in url:
                url = url.replace(':5432/', ':6543/')
            return url
        
        # Build connection string from individual parameters
        if all([self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.DB_NAME]):
            port = '6543' if use_pooling else self.DB_PORT
            return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{port}/{self.DB_NAME}"
        
        return None
    
    def get_db_params(self):
        """Get database connection parameters as a dictionary"""
        return {
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'dbname': self.DB_NAME
        }
