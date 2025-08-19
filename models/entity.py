from sqlalchemy import Column, Integer, String, DateTime
from database.connection import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    managers = relationship("Manager", back_populates="entity", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="entity", cascade="all, delete-orphan")
    raffle_sets = relationship("RaffleSet", back_populates="entity", cascade="all, delete-orphan", overlaps="projects")
    raffles = relationship("Raffle", back_populates="entity", cascade="all, delete-orphan", overlaps="projects,raffle_sets")
    buyers = relationship("Buyer", back_populates="entity", cascade="all, delete-orphan", overlaps="created_by_manager")
