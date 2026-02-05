from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.database.models import User


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession, email: str, password: str, is_superuser: bool
) -> User:
    # #region agent log
    import json
    with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"B","location":"user.py:13","message":"create_user entry","data":{"password_len_chars":len(password),"password_len_bytes":len(password.encode('utf-8'))},"timestamp":1733456789002})+'\n')
    # #endregion
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        is_superuser=is_superuser,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await get_user_by_email(db, email)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
