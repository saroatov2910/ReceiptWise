import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(str, enum.Enum):
    food = "food"
    transport = "transport"
    office = "office"
    utilities = "utilities"
    entertainment = "entertainment"
    health = "health"
    other = "other"


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    vendor = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    currency = Column(String, default="ILS")
    date = Column(String, nullable=True)
    category = Column(Enum(Category), default=Category.other)
    description = Column(Text, nullable=True)

    image_url = Column(String, nullable=True)   # S3 URL
    raw_text = Column(Text, nullable=True)       # טקסט גולמי מה-OCR

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="receipts")
