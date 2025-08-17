from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, ForeignKeyConstraint
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class RaffleSet(Base):
    __tablename__ = "raffle_sets"

    # Primary Key compuesta
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    set_number = Column(Integer, primary_key=True)  # Auto-increment por proyecto

    # Campos de datos
    name = Column(String(60), nullable=False)
    type = Column(String(8), nullable=False)  # 'online' o 'physical'
    init = Column(Integer, nullable=False)  # Número inicial de rifas
    final = Column(Integer, nullable=False)  # Número final de rifas
    unit_price = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints y Foreign Keys compuestas
    __table_args__ = (
        CheckConstraint("type IN ('online', 'physical')", name='check_type'),
        CheckConstraint("init <= final", name='check_valid_numbers'),
        ForeignKeyConstraint(['user_id', 'project_number'], ['projects.user_id', 'projects.project_number']),
    )

    # Relaciones con overlaps específicos según warnings de SQLAlchemy
    project = relationship("Project", back_populates="raffle_sets", overlaps="raffle_sets")
    user = relationship("User", back_populates="raffle_sets", overlaps="project,raffle_sets")
    raffles = relationship("Raffle", back_populates="raffle_set", cascade="all, delete-orphan", overlaps="raffles")
