from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from database.connection import Base  # Import central Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Project(Base):
    __tablename__ = "projects"

    # Composite Primary Key
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)  # Auto-increment per entity

    # Data fields
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships with specific overlaps according to SQLAlchemy warnings
    entity = relationship("Entity", back_populates="projects")
    raffle_sets = relationship("RaffleSet", back_populates="project", cascade="all, delete-orphan", overlaps="raffle_sets")
