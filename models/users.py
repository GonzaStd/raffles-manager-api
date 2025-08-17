from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database.connection import Base  # Importar Base central
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones con overlaps para evitar warnings de SQLAlchemy
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    raffle_sets = relationship("RaffleSet", back_populates="user", cascade="all, delete-orphan", overlaps="projects")
    raffles = relationship("Raffle", back_populates="user", cascade="all, delete-orphan", overlaps="projects,raffle_sets")
    buyers = relationship("Buyer", back_populates="user", cascade="all, delete-orphan")
