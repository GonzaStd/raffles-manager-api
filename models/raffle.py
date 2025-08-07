from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base


class Raffle(Base):
    __tablename__ = "raffles"
    number = Column(Integer, primary_key=True)
    set_id = Column(Integer, ForeignKey("raffle_sets.id"), nullable=False)
    buyer_id = Column(Integer, ForeignKey("buyers.id"))
    sell_date = Column(TIMESTAMP)
    payment_method = Column(String(8))
    state = Column(String(9), default="available")

    raffle_set = relationship("RaffleSet", back_populates="raffles")
    buyer = relationship("Buyer", back_populates="raffles")
