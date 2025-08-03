from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base

class RaffleSet(Base):
    __tablename__ = "raffle_sets"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(60), nullable=False)
    type = Column(String(8), nullable=False)
    init = Column(Integer, nullable=False)
    final = Column(Integer, nullable=False)
    unit_price = Column(Integer, nullable=False)
    creation_date = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    __table_args__ = (
        CheckConstraint("init < final", name="valid_numbers"),
    )

    project = relationship("Project", back_populates="raffle_sets")
    raffles = relationship("Raffle", back_populates="raffle_set")