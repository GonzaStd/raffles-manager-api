from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, func
from database.connection import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Buyer(Base):
    __tablename__ = "buyers"

    # Primary Key compuesta
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    buyer_number = Column(Integer, primary_key=True)  # Auto-increment por usuario

    # Campos de datos
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Constraint de unicidad: nombre-teléfono debe ser único por usuario
    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'phone', name='unique_buyer_name_phone_user'),
    )

    # Relaciones
    user = relationship("User", back_populates="buyers")
    raffles = relationship("Raffle", back_populates="buyer")
