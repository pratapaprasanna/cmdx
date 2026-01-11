"""
Initialize database with tables
"""
from app.db.base import Base, engine
from app.db.models import *  # noqa: F401, F403

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
