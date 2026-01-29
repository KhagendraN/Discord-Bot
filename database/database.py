import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

# Load .env file to ensure DATABASE_URL is available
from dotenv import load_dotenv
load_dotenv()

# Database URL configuration
# Priority: DATABASE_URL env var (PostgreSQL) > SQLite fallback
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Production: Use PostgreSQL from environment variable
    # Handle postgres:// vs postgresql:// (some providers use old format)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(DATABASE_URL)
else:
    # Local development: Use SQLite
    # Store DB file in /data if available (writable volume), or project root locally
    if os.path.exists('/data') and os.access('/data', os.W_OK):
        DB_NAME = '/data/class_data.db'
    else:
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        DB_NAME = os.path.join(ROOT, 'class_data.db')
    
    DATABASE_URL = f"sqlite:///{DB_NAME}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)

def init_db():
    """Initialize the database by creating all tables defined in models.py."""
    Base.metadata.create_all(bind=engine)
    
    # SQLite-specific migration: Add new columns if they don't exist
    # Only run this for SQLite databases
    if 'sqlite' in str(engine.url):
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
