from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, ForeignKeyConstraint
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Raffle(Base):
    __tablename__ = "raffles"

    # Composite Primary Key
    entity_id = Column(Integer, ForeignKey("entities.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    raffle_number = Column(Integer, primary_key=True)  # Auto-increment per project

    # Foreign Key compound to RaffleSet
    set_number = Column(Integer, nullable=False)  # Reference to set within project

    # Data fields
    buyer_entity_id = Column(Integer, nullable=True)  # Composite FK to Buyer
    buyer_number = Column(Integer, nullable=True)
    sold_by_entity_id = Column(Integer, nullable=True)  # Composite FK to Manager who sold it
    sold_by_manager_number = Column(Integer, nullable=True)
    payment_method = Column(String(8), nullable=True)  # 'cash', 'card', 'transfer'
    state = Column(String(9), default='available', nullable=False)  # 'available', 'sold', 'reserved'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints and composite Foreign Keys
    __table_args__ = (
        CheckConstraint("payment_method IN ('cash', 'card', 'transfer')", name='check_payment_method'),
        CheckConstraint("state IN ('available', 'sold', 'reserved')", name='check_state'),
        ForeignKeyConstraint(['entity_id', 'project_number', 'set_number'],
                             ['raffle_sets.entity_id', 'raffle_sets.project_number', 'raffle_sets.set_number']),
        ForeignKeyConstraint(['buyer_entity_id', 'buyer_number'],
                             ['buyers.entity_id', 'buyers.buyer_number']),
        ForeignKeyConstraint(['sold_by_entity_id', 'sold_by_manager_number'],
                             ['managers.entity_id', 'managers.manager_number']),
    )

    # Relationships with specific overlaps according to SQLAlchemy warnings
    raffle_set = relationship("RaffleSet", back_populates="raffles", overlaps="raffles")
    entity = relationship("Entity", back_populates="raffles", overlaps="raffle_set,raffles")
    buyer = relationship("Buyer", back_populates="raffles",
                         foreign_keys="[Raffle.buyer_entity_id, Raffle.buyer_number]")
    sold_by = relationship("Manager", back_populates="raffles_sold",
                           foreign_keys="[Raffle.sold_by_entity_id, Raffle.sold_by_manager_number]")