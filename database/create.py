from sqlalchemy import text, create_engine
from core.config_loader import settings
from pathlib import Path

structure_path = Path(__file__).resolve().parent / "structure.sql"

def get_sys_engine():
    """Create system engine for database operations"""
    return create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}")

def db_exists(db: str):
    sys_engine = get_sys_engine()
    with sys_engine.connect() as conn:
        result = conn.execute(text("SHOW DATABASES"))
        databases = [row[0] for row in result]
        return db in databases


def create_database():
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