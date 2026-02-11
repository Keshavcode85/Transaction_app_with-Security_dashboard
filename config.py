import os

class Config:
    """Base configuration for the Flask application"""

    # Basic Flask config
    SECRET_KEY = os.environ.get("SECRET_KEY") or "super-secret-key-change-this"

    # Database configuration (SQLite for simplicity)
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{os.path.join(BASE_DIR, 'transaction_app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session configuration
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"

    # Security & Suspicious Login Settings
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_ATTEMPT_WINDOW_MINUTES = 10
    HIGH_RISK_SCORE_THRESHOLD = 70

    # OTP configuration
    OTP_EXPIRY_MINUTES = 5
    OTP_LENGTH = 6

    # Email / Alert settings (can be extended later)
    ALERT_EMAIL_ENABLED = False
    ALERT_SMS_ENABLED = False

    # Application settings
    DEBUG = True
    ENV = "development"
