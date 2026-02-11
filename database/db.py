from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy instance
db = SQLAlchemy()


def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)

    with app.app_context():
        from database import models  # ensure models are registered
        db.create_all()
