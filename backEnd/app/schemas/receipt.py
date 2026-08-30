from pydantic import BaseModel
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
