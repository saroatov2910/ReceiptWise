from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.dependencies import require_user
from app.models.receipt import Receipt
from app.models.user import User
from app.schemas.receipt import ReceiptOut
from app.services.ocr import extract_text_from_image
from app.services.claude import parse_receipt_with_claude

router = APIRouter(prefix="/receipts", tags=["Receipts"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/tiff"}


@router.post("/upload", response_model=ReceiptOut, status_code=201)
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="סוג קובץ לא נתמך. השתמש ב-JPG/PNG/WEBP/TIFF")

    contents = await file.read()

    # שלב 1 — OCR
    raw_text = extract_text_from_image(contents)
    if not raw_text:
        raise HTTPException(status_code=422, detail="לא ניתן לחלץ טקסט מהתמונה")

    # שלב 2 — Claude מסווג את הנתונים
    try:
        parsed = parse_receipt_with_claude(raw_text)
    except Exception:
        parsed = {}

    receipt = Receipt(
        user_id=current_user.id,
        raw_text=raw_text,
        vendor=parsed.get("vendor"),
        amount=parsed.get("amount"),
        currency=parsed.get("currency", "ILS"),
        date=parsed.get("date"),
        category=parsed.get("category", "other"),
        description=parsed.get("description"),
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


@router.get("/", response_model=list[ReceiptOut])
def list_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    return db.query(Receipt).filter(Receipt.user_id == current_user.id).all()


@router.get("/{receipt_id}", response_model=ReceiptOut)
def get_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.user_id == current_user.id,
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="קבלה לא נמצאה")
    return receipt


@router.delete("/{receipt_id}", status_code=204)
def delete_receipt(
    receipt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.user_id == current_user.id,
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="קבלה לא נמצאה")
    db.delete(receipt)
    db.commit()
