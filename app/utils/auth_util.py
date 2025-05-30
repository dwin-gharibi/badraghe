from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.utils.jwt_util import decode_access_token
from app.db import execute_query
from app.db import connect_db, close_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    await connect_db()
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("user_id") or payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    user = await execute_query(
        "SELECT id, email, first_name, last_name FROM users WHERE id = %s",
        (user_id,),
        fetch_one=True
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not isinstance(user, dict):
        user = dict(zip(["id", "email", "first_name", "last_name"], user))

    return {
        "user_id": user["id"],
        "email": user["email"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name")
    }

def require_roles(*allowed_roles: str):
    async def role_checker(user=Depends(get_current_user)):
        await connect_db()
        roles = await execute_query(
            """
            SELECT r.name 
            FROM user_role ur 
            JOIN roles r ON ur.role_id = r.id 
            WHERE ur.user_id = %s
            """,
            (user["user_id"],),
            fetch_all=True
        )

        if roles:
            if isinstance(roles[0], tuple):
                user_roles = [r[0] for r in roles]
            else:
                user_roles = [r["name"] for r in roles]
        else:
            user_roles = []

        if not any(role in allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        return user
    return role_checker
