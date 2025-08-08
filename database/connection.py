from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config_loader import settings

DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI) #"mysql+pymysql://raffles-manager:raffles@localhost/raffles_draw"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()