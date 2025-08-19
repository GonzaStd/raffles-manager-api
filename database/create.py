from sqlalchemy import text, create_engine
from sqlalchemy.exc import ProgrammingError, OperationalError
from core.config_loader import settings
from database.connection import Base, engine
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

structure_path = Path(__file__).resolve().parent / "structure.sql"

IS_RAILWAY = getattr(settings, "ENVIRONMENT", "local").lower() == "railway"

def get_sys_engine():
    """Create system engine for database operations"""
    database_url = settings.SQLALCHEMY_DATABASE_URI

    if settings.DATABASE_URL or settings.MYSQL_URL:
        # Railway environment - connect directly to the database (it already exists)
        return create_engine(database_url)
    else:
        # Local environment - connect to server without database for creation
        return create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}:{settings.MARIADB_PORT}")

def check_tables_exist(verbose=False):
    """Check if all required tables exist, optionally log missing tables."""
    required_tables = ['entities', 'managers', 'projects', 'buyers', 'raffle_sets', 'raffles']
    missing = []
    try:
        with engine.connect() as conn:
            for table in required_tables:
                result = conn.execute(text(f"SHOW TABLES LIKE '{table}'"))
                if not result.fetchone():
                    missing.append(table)
            if missing:
                if verbose:
                    logger.error(f"Missing tables: {missing}")
                return False
            return True
    except Exception as e:
        logger.error(f"Error checking tables: {e}")
        return False

def create_tables_sqlalchemy():
    """Create tables using SQLAlchemy"""
    try:
        # Import models here to avoid circular imports
        from models.entity import Entity
        from models.manager import Manager
        from models.buyer import Buyer
        from models.project import Project
        from models.raffleset import RaffleSet
        from models.raffle import Raffle

        logger.info("Creating tables using SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully using SQLAlchemy")
        return True
    except Exception as e:
        logger.error(f"Error creating tables with SQLAlchemy: {e}")
        return False

def create_tables_sql():
    """Create tables using the SQL file as fallback, ensuring triggers are created after tables."""
    if not structure_path.exists():
        logger.error(f"SQL structure file not found: {structure_path}")
        return False

    try:
        with open(structure_path, 'r') as f:
            sql_content = f.read()

        # Split by DELIMITER to separate triggers
        sql_blocks = sql_content.split('DELIMITER')
        table_sql = sql_blocks[0]
        trigger_sql = ''
        if len(sql_blocks) > 1:
            trigger_sql = 'DELIMITER'.join(sql_blocks[1:])

        # Parse and execute table creation statements robustly
        with engine.connect() as conn:
            statement = ''
            for line in table_sql.splitlines():
                line = line.strip()
                # Skip comments and blank lines
                if not line or line.startswith('--'):
                    continue
                # Accumulate statement
                statement += ' ' + line
                # If statement ends with semicolon, execute it
                if line.endswith(';'):
                    try:
                        conn.execute(text(statement))
                    except Exception as e:
                        logger.error(f"Error executing statement: {e}\n[SQL: {statement}]")
                        return False
                    statement = ''
            conn.commit()

        # Validate table existence before creating triggers
        if not check_tables_exist(verbose=True):
            logger.error("Table creation failed, not all tables exist.")
            return False

        # Now execute triggers in a new connection to ensure tables are visible
        if trigger_sql:
            with engine.connect() as conn:
                # Remove DELIMITER and split by $$
                trigger_blocks = trigger_sql.replace('DELIMITER', '').split('$$')
                for trigger in trigger_blocks:
                    trigger = trigger.strip()
                    if trigger and 'CREATE TRIGGER' in trigger.upper():
                        conn.execute(text(trigger))
                conn.commit()

        logger.info("Tables and triggers created successfully using SQL file")
        return True

    except Exception as e:
        logger.error(f"Error creating tables with SQL file: {e}")
        return False

def print_db_structure():
    """Print the DB structure from structure.sql"""
    if structure_path.exists():
        with open(structure_path, 'r') as f:
            print(f.read())
    else:
        print(f"SQL structure file not found: {structure_path}")

def create_database_if_not_exists():
    """Create the database if it doesn't exist (only on localhost). On Railway, just print the DB structure."""
    if IS_RAILWAY:
        logger.info("Railway detected: Skipping DB creation, printing DB structure.")
        print_db_structure()
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
    """Create database and tables if they don't exist (only on localhost). On Railway, just print the DB structure."""
    if IS_RAILWAY:
        logger.info("Railway detected: Skipping DB creation, printing DB structure.")
        print_db_structure()
        return

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
                return create_database()
            else:
                raise Exception("Failed to create database")

        logger.error(f"Could not connect to database: {e}")

        # If we're in local development and there are access issues, try setup_mysql
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
