from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, func, ForeignKeyConstraint
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Buyer(Base):
    __tablename__ = "buyers"

    # Composite Primary Key
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    buyer_number = Column(Integer, primary_key=True)  # Auto-increment per entity

    # Data fields
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_manager_number = Column(Integer, nullable=False)

    # Uniqueness constraint: name-phone must be unique per entity
    __table_args__ = (
        UniqueConstraint('entity_id', 'name', 'phone', name='unique_buyer_name_phone_entity'),
        ForeignKeyConstraint(['entity_id', 'created_by_manager_number'], ['managers.entity_id', 'managers.manager_number'], name='fk_buyer_created_by_manager', ondelete='SET NULL'),
    )

    # Relationships
    entity = relationship("Entity", back_populates="buyers")
    raffles = relationship("Raffle", back_populates="buyer")
    created_by_manager = relationship(
        "Manager",
        foreign_keys="[Buyer.entity_id, Buyer.created_by_manager_number]",
        back_populates="buyers_created",
        overlaps="entity"
    )
