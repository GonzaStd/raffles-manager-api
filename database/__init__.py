from database.create import create_database
from database.connection import engine, SessionLocal, Base

# Importar todos los modelos para asegurar que estén registrados
from models.users import User
from models.project import Project
from models.buyer import Buyer
from models.raffleset import RaffleSet
from models.raffle import Raffle

# Create tables on startup with better error handling
try:
    create_database()
    print("Database initialized successfully")
except Exception as e:
    print(f"Warning: Could not create database/tables: {e}")
    # Continue anyway - tables might already exist or will be created later
