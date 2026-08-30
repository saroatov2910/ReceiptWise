from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, UserOut, Token, ChangePassword
from app.auth.jwt import hash_password, verify_password, create_access_token
from app.auth.dependencies import require_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(require_user)):
    return current_user


@router.post("/me/change-password", status_code=204)
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user),
):
    if not verify_password(data.old_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="סיסמה ישנה שגויה")
    current_user.hashed_password = hash_password(data.new_password)
    db.commit()


# Register a new user
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# User login
@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token}

