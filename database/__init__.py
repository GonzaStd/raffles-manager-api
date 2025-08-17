from database.create import create_database_if_not_exists
from database.connection import engine, SessionLocal, Base

# Importar todos los modelos para asegurar que estén registrados
from models.users import User
from models.project import Project
from models.buyer import Buyer
from models.raffleset import RaffleSet
from models.raffle import Raffle

# Initialize database only when explicitly called
def initialize_database():
    """Initialize database and tables - call this explicitly when needed"""
    try:
        # First ensure database exists
        if create_database_if_not_exists():
            # Then create tables using SQLAlchemy
            Base.metadata.create_all(bind=engine)
            print("Database initialized successfully")
            return True
    except Exception as e:
        print(f"Warning: Could not create database/tables: {e}")
        return False

# Try to initialize during import, but don't fail if database doesn't exist
try:
    # First ensure the database exists
    if create_database_if_not_exists():
        # Then create tables using SQLAlchemy
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully")
    else:
        print("Warning: Could not create database")
except Exception as e:
    print(f"Warning: Could not create database/tables: {e}")
    # Continue anyway - database will be created when first accessed
