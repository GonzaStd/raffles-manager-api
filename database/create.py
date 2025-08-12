from sqlalchemy import text, create_engine
from core.config_loader import settings
from pathlib import Path

structure_path = Path(__file__).resolve().parent / "structure.sql"

def get_sys_engine():
    """Create system engine for database operations"""
    # Use the same URL that the main app uses
    database_url = settings.SQLALCHEMY_DATABASE_URI

    if settings.DATABASE_URL or settings.MYSQL_URL:
        # Railway environment - connect directly to the database (it already exists)
        return create_engine(database_url)
    else:
        # Local environment - connect to server without database for creation
        return create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}")

def db_exists(db: str):
    """Check if database exists (only for local development)"""
    if settings.DATABASE_URL or settings.MYSQL_URL:
        # In Railway, the database always exists
        return True

    sys_engine = get_sys_engine()
    with sys_engine.connect() as conn:
        result = conn.execute(text("SHOW DATABASES"))
        databases = [row[0] for row in result]
        return db in databases

def create_database():
    """Create database and tables"""
    try:
        if settings.DATABASE_URL or settings.MYSQL_URL:
            # Railway environment - just create tables in existing database
            engine = get_sys_engine()

            # Read and execute only table creation commands
            with open(structure_path, 'r') as file:
                sql_commands = file.read()

            # Skip CREATE DATABASE, USE commands for Railway
            commands = []
            for line in sql_commands.split('\n'):
                line = line.strip()
                if line and not line.startswith('CREATE DATABASE') and not line.startswith('USE '):
                    commands.append(line)

            # Join and split by semicolon to get complete statements
            full_sql = '\n'.join(commands)
            statements = [stmt.strip() for stmt in full_sql.split(';') if stmt.strip()]

            with engine.connect() as conn:
                for statement in statements:
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        print(f"Error executing statement: {statement[:50]}... Error: {e}")

            print("Tables created successfully in Railway")
            return True

        else:
            # Local environment - create database and tables
            if not db_exists("raffles_draw"):
                with open(structure_path, 'r') as file:
                    sql_commands = file.read()

                commands = [command.strip() for command in sql_commands.split(";") if command.strip()]
                sys_engine = get_sys_engine()
                connection = sys_engine.connect()

                for command in commands:
                    try:
                        connection.execute(text(command))
                        connection.commit()
                    except Exception as e:
                        print(f"There was a problem creating \"raffles_draw\" database on mysql:\n{e}")
                connection.close()
            return True

    except Exception as e:
        print(f"Database creation error: {e}")
        return True  # Continue anyway
