from database.create import create_database
if create_database():
    from database.connection import engine, SessionLocal, Base

