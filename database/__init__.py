from database.create import create_database_if_not_exists, create_tables_sql, check_tables_exist
from database.connection import engine, SessionLocal, Base

# Initialize database only when explicitly called
# Only use SQL file for table creation

def initialize_database():
    """Initialize database and tables - call this explicitly when needed"""
    try:
        # First ensure database exists (Railway: just prints structure)
        if create_database_if_not_exists():
            # Only create tables if missing
            if not check_tables_exist():
                create_tables_sql()
                print("Database tables created successfully using SQL file")
            else:
                print("Database and tables already exist. Skipping creation.")
            return True
    except Exception as e:
        print(f"Warning: Could not create database/tables: {e}")
        return False

# Remove any automatic SQLAlchemy table creation
# Only use SQL file for table creation
