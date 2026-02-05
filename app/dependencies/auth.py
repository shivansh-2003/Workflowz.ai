from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.models import User
from app.database.session import get_db
from app.dependencies.tenancy import OrgContext, get_org_context
from app.schemas.auth import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as exc:
        raise credentials_exception from exc

    result = await db.execute(select(User).where(User.email == token_data.email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required",
        )
    return current_user


async def get_current_org_head(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgContext:
    org_context = await get_org_context(db, current_user)
    if org_context.position != "head":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization head access required",
        )
    return org_context


async def get_current_member_with_org(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrgContext:
    return await get_org_context(db, current_user)
