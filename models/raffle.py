from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, ForeignKeyConstraint
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Raffle(Base):
    __tablename__ = "raffles"

    # Primary Key compuesta
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    project_number = Column(Integer, primary_key=True)
    raffle_number = Column(Integer, primary_key=True)  # Auto-increment por proyecto

    # Foreign Key compuesta hacia RaffleSet
    set_number = Column(Integer, nullable=False)  # Referencia al set dentro del proyecto

    # Campos de datos
    buyer_user_id = Column(Integer, nullable=True)  # FK compuesta hacia Buyer
    buyer_number = Column(Integer, nullable=True)
    payment_method = Column(String(8), nullable=True)  # 'cash', 'card', 'transfer'
    state = Column(String(9), default='available', nullable=False)  # 'available', 'sold', 'reserved'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraints y Foreign Keys compuestas
    __table_args__ = (
        CheckConstraint("payment_method IN ('cash', 'card', 'transfer')", name='check_payment_method'),
        CheckConstraint("state IN ('available', 'sold', 'reserved')", name='check_state'),
        ForeignKeyConstraint(['user_id', 'project_number', 'set_number'],
                             ['raffle_sets.user_id', 'raffle_sets.project_number', 'raffle_sets.set_number']),
        ForeignKeyConstraint(['buyer_user_id', 'buyer_number'],
                             ['buyers.user_id', 'buyers.buyer_number']),
    )

    # Relaciones con overlaps específicos según warnings de SQLAlchemy
    raffle_set = relationship("RaffleSet", back_populates="raffles", overlaps="raffles")
    user = relationship("User", back_populates="raffles", overlaps="raffle_set,raffles")
    buyer = relationship("Buyer", back_populates="raffles")
