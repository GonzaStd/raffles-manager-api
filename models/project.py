from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(60), nullable=False, unique=True)
    description = Column(Text)
    creation_date = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
    is_active = Column(Boolean, default=True)

    raffle_sets = relationship("RaffleSet", back_populates="project")
    user = relationship("Users", back_populates="projects")