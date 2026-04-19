from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import get_db, LoginDetail

router = APIRouter()


class VisitorIn(BaseModel):
    name: str
    email: EmailStr
    phone: str


class VisitorOut(BaseModel):
    message: str
    name: str
    role_id: int
    id: int  # Added user id to response


@router.post("/login", response_model=VisitorOut)
def login(data: VisitorIn, db: Session = Depends(get_db)):
    if not data.name.strip() or not data.phone.strip():
        raise HTTPException(status_code=400, detail="All fields are required.")

    phone = data.phone.strip()
    if not phone.startswith("+91"):
        phone = "+91" + phone

    # Check if email or phone already exists
    existing = db.query(LoginDetail).filter(
        (LoginDetail.email == data.email) | (LoginDetail.phone == phone)
    ).first()

    if existing:
        return VisitorOut(
            message="Welcome back!",
            name=existing.name,
            role_id=existing.role_id,
            id=existing.id  # Return user id
        )

    record = LoginDetail(
        name=data.name.strip(),
        email=data.email,
        phone=phone,
        role_id=2  # Default role for regular users
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return VisitorOut(
        message="Welcome!",
        name=data.name.strip(),
        role_id=record.role_id,
        id=record.id  # Return new user's id
    )


@router.get("/visitors")
def get_visitors(db: Session = Depends(get_db)):
    visitors = db.query(LoginDetail).all()
    return [
        {
            "id": v.id,
            "name": v.name,
            "email": v.email,
            "phone": v.phone,
            "visited_at": v.visited_at.isoformat(),
            "role_id": v.role_id,
        }
        for v in visitors
    ]
