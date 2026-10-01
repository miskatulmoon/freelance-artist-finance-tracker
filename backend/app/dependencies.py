from fastapi import HTTPException, Request, status
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

limiter = Limiter(key_func=get_remote_address)


def require_api_key(request: Request):
    settings = get_settings()
    api_key = settings.api_key
    if not api_key:
        # No API key configured - allow for single-user dev mode
        return
    provided = request.headers.get("X-API-Key")
    if not provided or provided != api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


def validate_chat_length(request_body_question: str):
    settings = get_settings()
    max_len = settings.chat_max_length
    # Enforce beyond Pydantic: strip and check byte length
    if len(request_body_question.strip()) > max_len:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Question too long")
