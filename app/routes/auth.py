from pydantic import BaseModel, EmailStr
from app.redis import get_redis, close_redis
from app.utils.jwt_util import create_access_token
from app.db import connect_db, close_db , execute_query
from fastapi import APIRouter, Request, HTTPException, status, Depends
from app.utils.security_util import hash_password
import random

router = APIRouter()

class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str

class OTPRequest(BaseModel):
    email_or_phone: str

class OTPVerify(BaseModel):
    email_or_phone: str
    otp_code: str

async def send_otp_via_email_or_sms(destination: str, otp: str):
    print(f"Sending OTP {otp} to {destination}")

@router.post("/send-otp")
async def send_otp(data: OTPRequest):
    redis = await get_redis()
    await connect_db()
    otp = f"{random.randint(100000, 999999)}"
    await redis.set(f"otp:{data.email_or_phone}", otp, ex=300)
    await send_otp_via_email_or_sms(data.email_or_phone, otp)
    await close_db()
    return {"msg": "OTP sent"}

@router.post("/verify-otp")
async def verify_otp(data: OTPVerify):
    redis = await get_redis()
    await connect_db()
    stored_otp = await redis.get(f"otp:{data.email_or_phone}")
    if not stored_otp or stored_otp != data.otp_code:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = await execute_query(
        "SELECT id FROM users WHERE email = %s OR phone = %s", 
        (data.email_or_phone, data.email_or_phone),
        fetch_one=True
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_access_token({"user_id": user["id"]})
    await close_db()

    return {"access_token": token, "token_type": "bearer"}

@router.post("/signup")
async def signup(request: Request):
    data = await request.json()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not all([first_name, last_name, email, phone, password]):
        raise HTTPException(status_code=400, detail="Missing required fields")

    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short")

    await connect_db()

    existing_user = await execute_query(
        "SELECT id FROM users WHERE email = %s", (email,), fetch_one=True
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_phone = await execute_query(
        "SELECT id FROM users WHERE phone = %s", (phone,), fetch_one=True
    )
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    hashed_pw = hash_password(password)

    insert_query = """
    INSERT INTO users (first_name, last_name, email, phone, password)
    VALUES (%s, %s, %s, %s, %s)
    """

    user_id = await execute_query(insert_query, (first_name, last_name, email, phone, hashed_pw))

    token = create_access_token({"sub": email})

    await close_db()

    return {"access_token": token, "token_type": "bearer", "user_id": user_id}