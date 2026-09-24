from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import InvalidTokenError, decode_token
from app.database import get_db
from app.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def _resolve_user(token: str | None, db: Session) -> User:
    if token is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        user_id = decode_token(token, expected_type="access")
    except InvalidTokenError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials if credentials else None
    return _resolve_user(token, db)


def get_current_user_from_header_or_query(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    token: str | None = None,
    db: Session = Depends(get_db),
) -> User:
    """Same as get_current_user, but also accepts ?token=... — needed for
    <img> tags, which cannot send an Authorization header."""
    resolved = credentials.credentials if credentials else token
    return _resolve_user(resolved, db)
