from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime, text
from database.connection import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)  # Fixed to match SQL
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    creation_date: Mapped[DateTime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)  # Fixed field name
    updated_at: Mapped[DateTime] = mapped_column(DateTime, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    projects = relationship("Project", back_populates="user")
