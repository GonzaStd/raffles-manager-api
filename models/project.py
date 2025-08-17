from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from database.connection import Base  # Importar Base central
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Project(Base):
    __tablename__ = "projects"

    # Primary Key compuesta
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)  # Auto-increment por usuario

    # Campos de datos
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones con overlaps específicos según warnings de SQLAlchemy
    user = relationship("User", back_populates="projects")
    raffle_sets = relationship("RaffleSet", back_populates="project", cascade="all, delete-orphan", overlaps="raffle_sets")
