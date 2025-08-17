from sqlalchemy import text, create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
from core.config_loader import settings
from database.connection import Base, engine
from pathlib import Path
import logging

# Importar TODOS los modelos explícitamente para que SQLAlchemy los reconozca
from models.users import User
from models.project import Project
from models.buyer import Buyer
from models.raffleset import RaffleSet
from models.raffle import Raffle

logger = logging.getLogger(__name__)

structure_path = Path(__file__).resolve().parent / "structure.sql"

def get_sys_engine():
    """Create system engine for database operations"""
    database_url = settings.SQLALCHEMY_DATABASE_URI

    if settings.DATABASE_URL or settings.MYSQL_URL:
        # Railway environment - connect directly to the database (it already exists)
        return create_engine(database_url)
    else:
        # Local environment - connect to server without database for creation
        return create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}:{settings.MARIADB_PORT}")

def check_tables_exist():
    """Check if all required tables exist"""
    required_tables = ['users', 'projects', 'buyers', 'raffle_sets', 'raffles']

    try:
        with engine.connect() as conn:
            # Check each table
            for table in required_tables:
                result = conn.execute(text(f"SHOW TABLES LIKE '{table}'"))
                if not result.fetchone():
                    logger.info(f"Table '{table}' does not exist")
                    return False

            logger.info("All required tables exist")
            return True
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False

def create_tables_sqlalchemy():
    """Create tables using SQLAlchemy"""
    try:
        logger.info("Creating tables using SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully using SQLAlchemy")
        return True
    except Exception as e:
        logger.error(f"Error creating tables with SQLAlchemy: {e}")
        return False

def create_tables_sql():
    """Create tables using the SQL file as fallback"""
    if not structure_path.exists():
        logger.error(f"SQL structure file not found: {structure_path}")
        return False

    try:
        with open(structure_path, 'r') as f:
            sql_content = f.read()

        # Execute SQL commands
        with engine.connect() as conn:
            # Split by delimiter changes and execute
            sql_commands = sql_content.split('DELIMITER')

            for i, command_block in enumerate(sql_commands):
                if i == 0:
                    # First block - normal SQL commands
                    commands = [cmd.strip() for cmd in command_block.split(';') if cmd.strip()]
                    for cmd in commands:
                        if cmd.upper().startswith(('CREATE', 'USE', 'INSERT')):
                            conn.execute(text(cmd))
                elif '$$' in command_block:
                    # Trigger blocks
                    triggers = command_block.split('$$')
                    for trigger in triggers:
                        trigger = trigger.strip()
                        if trigger and 'CREATE TRIGGER' in trigger.upper():
                            conn.execute(text(trigger))

            conn.commit()
            logger.info("Tables created successfully using SQL file")
            return True

    except Exception as e:
        logger.error(f"Error creating tables with SQL file: {e}")
        return False

def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    if settings.DATABASE_URL or settings.MYSQL_URL:
        # Railway environment - database should already exist
        logger.info("Using external database service, skipping database creation")
        return True

    try:
        # Connect to MySQL server without specifying database
        sys_engine = create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}:{settings.MARIADB_PORT}")

        with sys_engine.connect() as conn:
            # Create database if it doesn't exist
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MARIADB_DATABASE}"))
            conn.commit()
            logger.info(f"Database '{settings.MARIADB_DATABASE}' created or already exists")
            return True

    except Exception as e:
        logger.error(f"Error creating database: {e}")
        return False

def create_database():
    """Create database and tables if they don't exist"""
    try:
        # First, ensure the database exists
        if not create_database_if_not_exists():
            raise Exception("Failed to create database")

        # Test connection to the database
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")

        # Check if tables exist
        if check_tables_exist():
            logger.info("All tables already exist, skipping creation")
            return

        # Try SQLAlchemy first
        if create_tables_sqlalchemy():
            # Verify tables were created
            if check_tables_exist():
                logger.info("Database tables created successfully with SQLAlchemy")
                return

        # Fallback to SQL file
        logger.info("SQLAlchemy method failed or incomplete, trying SQL file...")
        if create_tables_sql():
            if check_tables_exist():
                logger.info("Database tables created successfully with SQL file")
                return

        # If we get here, both methods failed
        raise Exception("Failed to create tables with both SQLAlchemy and SQL file methods")

    except OperationalError as e:
        if "Unknown database" in str(e):
            logger.error(f"Database {settings.MARIADB_DATABASE} does not exist and could not be created")
            logger.info("Attempting to create database...")
            if create_database_if_not_exists():
                logger.info("Database created, retrying table creation...")
                # Retry after database creation
                return create_database()
            else:
                raise Exception("Failed to create database")

        logger.error(f"Could not connect to database: {e}")

        # Si estamos en desarrollo local y hay problemas de acceso, intentar setup_mysql
        if not (settings.DATABASE_URL or settings.MYSQL_URL):
            if "Access denied" in str(e) or "Connection refused" in str(e):
                logger.info("Attempting to setup MySQL for local development...")
                try:
                    from core.database import setup_mysql
                    if setup_mysql():
                        logger.info("MySQL setup completed, retrying connection...")
                        # Retry after setup
                        create_database()
                        return
                except Exception as setup_error:
                    logger.error(f"MySQL setup failed: {setup_error}")

        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating database: {e}")
        raise e
