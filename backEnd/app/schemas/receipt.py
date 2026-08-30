from pydantic import BaseModel
from typing import Optional
from app.models.receipt import Category


class ReceiptOut(BaseModel):
    id: int
    vendor: str | None
    amount: float | None
    currency: str
    date: str | None
    category: Category
    description: str | None
    image_url: str | None
    raw_text: str | None

    model_config = {"from_attributes": True}


class ReceiptUpdate(BaseModel):
    vendor: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    date: Optional[str] = None
    category: Optional[Category] = None
    description: Optional[str] = None


class CategoryStat(BaseModel):
    category: str
    total: float
    count: int


class StatsOut(BaseModel):
    total_amount: float
    total_count: int
    by_category: list[CategoryStat]
    by_month: list[dict]

