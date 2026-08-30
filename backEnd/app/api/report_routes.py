from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import require_user
from app.models.receipt import Receipt
from app.models.user import User
from app.services.report import generate_pdf_report

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/monthly")
def monthly_report(
    month: str = Query(..., description="פורמט: YYYY-MM, לדוגמה 2026-08"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    receipts = db.query(Receipt).filter(
        Receipt.user_id == current_user.id,
        Receipt.date.like(f"{month}%"),
    ).all()

    pdf_bytes = generate_pdf_report(
        receipts=receipts,
        month=month,
        user_name=current_user.full_name or current_user.email,
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{month}.pdf"},
    )
