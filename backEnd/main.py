from fastapi import FastAPI
from app.core.database import Base, engine
from app.api.auth_routes import router as auth_router
from app.api.receipt_routes import router as receipt_router
from app.api.report_routes import router as report_router
import app.models.receipt  # noqa: ensure Receipt table is created

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ReceiptWise API")

app.include_router(auth_router)
app.include_router(receipt_router)
app.include_router(report_router)


@app.get("/")
def root():
    return {"message": "ReceiptWise API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
