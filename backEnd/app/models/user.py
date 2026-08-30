import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"
    guest = "guest"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
