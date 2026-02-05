from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from .config import settings

# Initialize CryptContext with bcrypt
# Use explicit bcrypt configuration to avoid initialization issues
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError as e:
        # If passlib fails due to initialization bug detection, fall back to direct bcrypt
        if "72 bytes" in str(e) or "longer than 72" in str(e):
            # Check if user's password actually exceeds 72 bytes
            pwd_byte_len = len(plain_password.encode('utf-8'))
            if pwd_byte_len > 72:
                return False  # Password too long, can't verify
            # Otherwise, this is passlib's internal bug detection failing
            # Fall back to direct bcrypt verification
            import bcrypt
            try:
                # hashed_password is already a string from DB, convert to bytes if needed
                hash_bytes = hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
                return bcrypt.checkpw(plain_password.encode('utf-8'), hash_bytes)
            except Exception:
                return False
        # For other ValueError cases, re-raise
        raise


def get_password_hash(password: str) -> str:
    # #region agent log
    import json
    pwd_bytes = password.encode('utf-8')
    pwd_byte_len = len(pwd_bytes)
    with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"security.py:16","message":"get_password_hash entry","data":{"password_len_chars":len(password),"password_len_bytes":pwd_byte_len,"exceeds_72":pwd_byte_len>72},"timestamp":1733456789003})+'\n')
    # #endregion
    if pwd_byte_len > 72:
        # #region agent log
        with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"security.py:19","message":"password exceeds 72 bytes - raising error","data":{"password_len_bytes":pwd_byte_len},"timestamp":1733456789004})+'\n')
        # #endregion
        raise ValueError("Password cannot exceed 72 bytes (bcrypt limitation)")
    # #region agent log
    with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"security.py:21","message":"calling pwd_context.hash","data":{"password_len_bytes":pwd_byte_len},"timestamp":1733456789005})+'\n')
    # #endregion
    try:
        result = pwd_context.hash(password)
    except ValueError as e:
        # #region agent log
        with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"security.py:36","message":"bcrypt hash failed","data":{"error":str(e),"password_len_bytes":pwd_byte_len},"timestamp":1733456789007})+'\n')
        # #endregion
        # If error is about password length AND user's password actually exceeds 72 bytes, re-raise
        if ("72 bytes" in str(e) or "longer than 72" in str(e)) and pwd_byte_len > 72:
            raise ValueError(f"Password too long: {pwd_byte_len} bytes (bcrypt limit is 72 bytes)")
        # Otherwise, this is likely a passlib initialization issue (bug detection uses test password)
        # Fall back to direct bcrypt
        import bcrypt
        # #region agent log
        with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"D","location":"security.py:43","message":"falling back to direct bcrypt","data":{"password_len_bytes":pwd_byte_len},"timestamp":1733456789008})+'\n')
        # #endregion
        salt = bcrypt.gensalt()
        result = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    # #region agent log
    with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"C","location":"security.py:43","message":"get_password_hash success","data":{},"timestamp":1733456789006})+'\n')
    # #endregion
    return result


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
