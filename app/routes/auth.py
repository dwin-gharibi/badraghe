from pydantic import BaseModel, EmailStr
from app.redis import get_redis, close_redis
from app.utils.jwt_util import create_access_token
from app.db import connect_db, close_db , execute_query
from fastapi import APIRouter, Request, HTTPException, status, Depends
from app.utils.security_util import hash_password
import random
import re
from app.utils.sms_util import send_sms_ir_otp

router = APIRouter()

class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp_code: str

def is_valid_iranian_number(phone: str) -> bool:
    return re.match(r"^\+989\d{9}$", phone) is not None

@router.post("/send-otp")
async def send_otp(data: OTPRequest):
    redis = await get_redis()

    if not is_valid_iranian_number(data.phone):
        raise HTTPException(status_code=400, detail="Invalid Iranian phone number format. Use +98 format.")

    limit_key = f"otp_limit:{data.phone}"
    attempts = await redis.get(limit_key)
    attempts = int(attempts or 0)

    if attempts >= 5:
        raise HTTPException(status_code=429, detail="OTP limit reached. Try again in 1 hour.")

    otp = f"{random.randint(100000, 999999)}"
    await redis.set(f"otp:{data.phone}", otp, ex=300)

    await redis.incr(limit_key)
    await redis.expire(limit_key, 3600)

    sms_ir_result = await send_sms_ir_otp(data.phone, otp)

    return {"msg": f"OTP sent {otp}", "sms_ir_result": sms_ir_result}

@router.post("/verify-otp")
async def verify_otp(data: OTPVerify):
    redis = await get_redis()
    await connect_db()
    stored_otp = await redis.get(f"otp:{data.phone}")
    if not stored_otp or stored_otp != data.otp_code:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = await execute_query(
        "SELECT id FROM users WHERE email = %s OR phone = %s", 
        (data.phone, data.phone),
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