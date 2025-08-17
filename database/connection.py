from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config_loader import settings
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# Crear el engine de la base de datos
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,  # Cambié de database_url a SQLALCHEMY_DATABASE_URI
    echo=False,  # Cambiar a True para ver las queries SQL
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency to get database session for FastAPI.
    """
    db = SessionLocal()
    try:
        # Test de conexión antes de usar la sesión
        db.execute(text("SELECT 1"))
        yield db
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_tables():
    """Crear todas las tablas en la base de datos"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise
