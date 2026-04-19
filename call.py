import os
import requests
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, LoginDetail
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

VAPI_API_KEY = os.getenv("VAPI_API_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID")


class CallRequest(BaseModel):
    phone: str  # e.g. "+911234567890"


@router.post("/call")
def make_call(data: CallRequest, db: Session = Depends(get_db)):
    # Check if phone exists in login_details
    visitor = db.query(LoginDetail).filter(LoginDetail.phone == data.phone).first()
    if not visitor:
        raise HTTPException(status_code=404, detail="Phone number not found in database.")

    # Ensure E.164 format — prepend +91 if no country code
    phone = data.phone.strip()
    if not phone.startswith("+"):
        phone = "+91" + phone

    payload = {
        "assistantId": VAPI_ASSISTANT_ID,
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": phone,
            "name": visitor.name,
        },
    }

    response = requests.post(
        "https://api.vapi.ai/call/phone",
        json=payload,
        headers={
            "Authorization": f"Bearer {VAPI_API_KEY}",
            "Content-Type": "application/json",
        },
    )

    if response.status_code not in (200, 201):
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {"message": f"Call initiated to {visitor.name} at {phone}", "vapi": response.json()}
