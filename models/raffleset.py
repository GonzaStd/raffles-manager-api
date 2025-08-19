from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, ForeignKeyConstraint
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class RaffleSet(Base):
    __tablename__ = "raffle_sets"

    # Composite Primary Key
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    set_number = Column(Integer, primary_key=True)  # Auto-increment per project

    # Data fields
    name = Column(String(60), nullable=False)
    type = Column(String(8), nullable=False)  # 'online' or 'physical'
    init = Column(Integer, nullable=False)  # Initial raffle number
    final = Column(Integer, nullable=False)  # Final raffle number
    unit_price = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints and composite Foreign Keys
    __table_args__ = (
        CheckConstraint("type IN ('online', 'physical')", name='check_type'),
        CheckConstraint("init <= final", name='check_valid_numbers'),
        ForeignKeyConstraint(['entity_id', 'project_number'], ['projects.entity_id', 'projects.project_number']),
    )

    # Relationships with specific overlaps according to SQLAlchemy warnings
    project = relationship("Project", back_populates="raffle_sets", overlaps="raffle_sets")
    entity = relationship("Entity", back_populates="raffle_sets", overlaps="project,raffle_sets")
    raffles = relationship("Raffle", back_populates="raffle_set", cascade="all, delete-orphan", overlaps="raffles")
