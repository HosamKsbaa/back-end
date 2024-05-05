

from fastapi import FastAPI, HTTPException, APIRouter, Body, status
from typing import List
from pydantic import BaseModel, EmailStr
import uvicorn



class AuthRequest(BaseModel):
    phone_number: str

class VerifyRequest(BaseModel):
    phone_number: str
    verification_code: str


auth_router = APIRouter()

@auth_router.post("/login", tags=["Authentication"])
async def login(auth_request: AuthRequest):
    # Here you would implement sending an SMS
    return {"message": "Verification code sent to " + auth_request.phone_number}

@auth_router.post("/verify", tags=["Authentication"])
async def verify(verify_request: VerifyRequest):
    # Here you would verify the code
    return {"message": "User verified", "token": "fake-jwt-token"}