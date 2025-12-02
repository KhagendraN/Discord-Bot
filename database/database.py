import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# Store DB file in project root to keep it outside the package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_NAME = os.path.join(ROOT, 'class_data.db')
DATABASE_URL = f"sqlite:///{DB_NAME}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session for thread safety if needed, though discord.py is async, 
# we usually use a fresh session per command or a context manager.
ScopedSession = scoped_session(SessionLocal)

def init_db():
    """Initialize the database by creating all tables defined in models.py."""
    Base.metadata.create_all(bind=engine)
    
    # Migration: Add new columns if they don't exist
    with engine.connect() as conn:
        # Check schedule table columns
        result = conn.execute(text("PRAGMA table_info(schedule)"))
        columns = [row.name for row in result]
        
        if 'instructor' not in columns:
            conn.execute(text("ALTER TABLE schedule ADD COLUMN instructor TEXT"))
        if 'note' not in columns:
            conn.execute(text("ALTER TABLE schedule ADD COLUMN note TEXT"))
        conn.commit()

def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
