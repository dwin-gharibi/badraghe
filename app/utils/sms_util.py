import httpx
from fastapi import HTTPException
from app.config import settings

async def send_sms_ir_otp(phone_number: str, otp: str):
    url = "https://api.sms.ir/v1/send/verify"
    
    payload = {
        "mobile": phone_number,
        "templateId": 123456,
        "parameters": [
            {
                "name": "code",
                "value": otp
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "text/plain",
        "x-api-key": settings.sms_ir_api_key
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="SMS.ir API request failed")

        return response.json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP via SMS: {str(e)}")
