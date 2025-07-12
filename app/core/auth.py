from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from pydantic import BaseModel

from app.core.config import Settings

oauth2_scheme = HTTPBearer()
settings = Settings()


class User(BaseModel):
    id: str
    email: str


def decode_supabase_jwt(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.get_supabase_jwt_secret(), algorithms=["HS256"], audience="authenticated")
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during token decoding: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def get_current_user(request: Request) -> User:
    user = request.state.user
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def check_request_user_id(request: Request, user_id: str | None):
    if settings.get_disable_auth():
        return
    user = get_current_user(request)
    
    if not user or user.id != str(user_id):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID does not match with authentication",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
