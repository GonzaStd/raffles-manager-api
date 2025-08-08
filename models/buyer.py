from sqlalchemy import Column, Integer, String, TIMESTAMP, UniqueConstraint, text
from sqlalchemy.orm import relationship
from database.connection import Base


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(64))
    register_date = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (
        UniqueConstraint('name', 'phone', name='unique_name_phone'),
    )

    raffles = relationship("Raffle", back_populates="buyer")
