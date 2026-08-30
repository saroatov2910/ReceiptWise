from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.auth.dependencies import require_user
from app.models.receipt import Receipt, Category
from app.models.user import User
from app.schemas.receipt import ReceiptOut, ReceiptUpdate, StatsOut, CategoryStat
from app.services.ocr import extract_text_from_image
from app.services.claude import parse_receipt_with_claude
from app.services.s3 import upload_image_to_s3, delete_image_from_s3
from app.core.config import settings

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

    # שלב 3 — העלאה ל-S3 (אם מוגדר)
    image_url = None
    if settings.AWS_BUCKET_NAME:
        try:
            image_url = upload_image_to_s3(contents, file.content_type)
        except Exception:
            pass  # S3 לא חובה — ממשיכים גם בלי

    receipt = Receipt(
        user_id=current_user.id,
        raw_text=raw_text,
        vendor=parsed.get("vendor"),
        amount=parsed.get("amount"),
        currency=parsed.get("currency", "ILS"),
        date=parsed.get("date"),
        category=parsed.get("category", "other"),
        description=parsed.get("description"),
        image_url=image_url,
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


@router.get("/stats", response_model=StatsOut)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    base = db.query(Receipt).filter(Receipt.user_id == current_user.id)

    total_amount = base.with_entities(func.coalesce(func.sum(Receipt.amount), 0)).scalar()
    total_count = base.count()

    # לפי קטגוריה
    by_category_rows = (
        base.with_entities(
            Receipt.category,
            func.coalesce(func.sum(Receipt.amount), 0).label("total"),
            func.count(Receipt.id).label("count"),
        )
        .group_by(Receipt.category)
        .all()
    )
    by_category = [
        CategoryStat(category=row.category.value, total=float(row.total), count=row.count)
        for row in by_category_rows
    ]

    # לפי חודש
    by_month_rows = (
        base.filter(Receipt.date.isnot(None))
        .with_entities(
            func.substr(Receipt.date, 1, 7).label("month"),
            func.coalesce(func.sum(Receipt.amount), 0).label("total"),
            func.count(Receipt.id).label("count"),
        )
        .group_by(func.substr(Receipt.date, 1, 7))
        .order_by(func.substr(Receipt.date, 1, 7))
        .all()
    )
    by_month = [
        {"month": row.month, "total": float(row.total), "count": row.count}
        for row in by_month_rows
    ]

    return StatsOut(
        total_amount=float(total_amount),
        total_count=total_count,
        by_category=by_category,
        by_month=by_month,
    )


@router.get("/", response_model=list[ReceiptOut])
def list_receipts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    return db.query(Receipt).filter(Receipt.user_id == current_user.id).order_by(Receipt.created_at.desc()).all()


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


@router.put("/{receipt_id}", response_model=ReceiptOut)
def update_receipt(
    receipt_id: int,
    data: ReceiptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id,
        Receipt.user_id == current_user.id,
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="קבלה לא נמצאה")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(receipt, field, value)

    db.commit()
    db.refresh(receipt)
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

    if receipt.image_url:
        delete_image_from_s3(receipt.image_url)

    db.delete(receipt)
    db.commit()



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
