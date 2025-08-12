from database.create import create_database
from database.connection import engine, SessionLocal, Base

# Create tables on startup
try:
    create_database()
except Exception as e:
    print(f"Warning: Could not create database/tables: {e}")
    # Continue anyway - tables might already exist
