from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, UniqueConstraint
from database.connection import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Manager(Base):
    __tablename__ = "managers"

    # Composite Primary Key
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    manager_number = Column(Integer, primary_key=True)  # Auto-increment per entity

    # Data fields (simplified as per SQL structure)
    username = Column(String(50), nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints: username must be unique per entity
    __table_args__ = (
        UniqueConstraint('entity_id', 'username', name='uk_manager_entity_username'),
    )

    # Relationships
    entity = relationship("Entity", back_populates="managers")
    raffles_sold = relationship("Raffle", back_populates="sold_by", foreign_keys="[Raffle.sold_by_entity_id, Raffle.sold_by_manager_number]")
    buyers_created = relationship(
        "Buyer",
        foreign_keys="[Buyer.entity_id, Buyer.created_by_manager_number]",
        back_populates="created_by_manager",
        overlaps="entity,buyers"
    )
