from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import SessionLocal, engine, Base
from database.models import User
from auth.auth import hash_password, verify_password, create_token
from auth.email_utils import generate_otp, send_otp_email

router = APIRouter()

# 🔥 OTP STORAGE
otp_storage = {}

# 🔥 VERIFIED EMAIL STORAGE
verified_emails = set()

Base.metadata.create_all(bind=engine)

# ---------------- SCHEMAS ----------------

class UserAuth(BaseModel):
    email: str
    password: str


class EmailSchema(BaseModel):
    email: str


class VerifyOTPSchema(BaseModel):
    email: str
    otp: str


# ---------------- DB ----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- SIGNUP OTP ----------------

@router.post("/send-otp")
def send_otp(
    data: EmailSchema,
    db: Session = Depends(get_db)
):

    email = data.email

    # 🔥 BLOCK EXISTING USERS
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Account already created"
        )

    otp = generate_otp()
    otp_storage[email] = otp

    print("🔥 SIGNUP OTP:", otp)

    try:
        send_otp_email(email, otp)

        return {
            "message": "OTP sent to email",
            "otp": otp
        }

    except Exception as e:

        print("❌ EMAIL ERROR:", e)

        return {
            "message": "OTP generated but email failed",
            "otp": otp
        }


# ---------------- RESET PASSWORD OTP ----------------

@router.post("/send-reset-otp")
def send_reset_otp(
    data: EmailSchema,
    db: Session = Depends(get_db)
):

    email = data.email

    # 🔥 CHECK ACCOUNT EXISTS
    existing_user = db.query(User).filter(
        User.email == email
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="Account does not exist"
        )

    otp = generate_otp()
    otp_storage[email] = otp

    print("🔥 RESET OTP:", otp)

    try:
        send_otp_email(email, otp)

        return {
            "message": "Reset OTP sent",
            "otp": otp
        }

    except Exception as e:

        print("❌ EMAIL ERROR:", e)

        return {
            "message": "OTP generated but email failed",
            "otp": otp
        }


# ---------------- VERIFY OTP ----------------

@router.post("/verify-otp")
def verify_otp(data: VerifyOTPSchema):

    email = data.email
    otp = data.otp

    if otp_storage.get(email) != otp:

        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    verified_emails.add(email)

    return {
        "message": "OTP verified"
    }


# ---------------- SIGNUP ----------------

@router.post("/signup")
def signup(
    user: UserAuth,
    db: Session = Depends(get_db)
):

    if user.email not in verified_emails:

        raise HTTPException(
            status_code=400,
            detail="Please verify OTP first"
        )

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing:

        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    new_user = User(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    verified_emails.discard(user.email)

    return {
        "message": "Signup successful"
    }


# ---------------- LOGIN ----------------

@router.post("/login")
def login(
    user: UserAuth,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing:

        raise HTTPException(
            status_code=401,
            detail="Account does not exist"
        )

    if not verify_password(
        user.password,
        existing.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

    token = create_token({
        "sub": existing.email
    })

    return {
        "access_token": token
    }


# ---------------- RESET PASSWORD ----------------

@router.post("/reset-password")
def reset_password(
    user: UserAuth,
    db: Session = Depends(get_db)
):

    existing = db.query(User).filter(
        User.email == user.email
    ).first()

    if not existing:

        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.email not in verified_emails:

        raise HTTPException(
            status_code=400,
            detail="Please verify OTP first"
        )

    existing.password = hash_password(
        user.password
    )

    db.commit()
    db.refresh(existing)

    verified_emails.discard(user.email)

    return {
        "message": "Password updated successfully"
    }