from sqlalchemy import text
from core import sys_engine
from pathlib import Path
structure_path = Path(__file__).resolve().parent / "structure.sql"

def db_exists(db: str):
    with sys_engine.connect() as conn:
        result = conn.execute(text("SHOW DATABASES"))
        databases = [row[0] for row in result]
        return db in databases


def create_database():
    if not db_exists("raffles_draw"):
        with open(structure_path, 'r') as file:
            sql_commands = file.read()

        commands = [command.strip() for command in sql_commands.split(";") if command.strip()]
        connection = sys_engine.connect()

        for command in commands:
            try:
                connection.execute(text(command))
                connection.commit()
            except Exception as e:
                print(f"There was a problem creating \"raffles_draw\" database on mysql:\n{e}")
    return True