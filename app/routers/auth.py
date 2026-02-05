from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.crud.user import authenticate_user, create_user, get_user_by_email
from app.database.session import get_db
from app.dependencies.auth import get_current_superuser
from app.database.models import User
from app.schemas.auth import Token, UserCreate, UserOut
from sqlalchemy import select

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.email, "is_superuser": user.is_superuser})
    return Token(access_token=access_token)


@router.post("/signup", response_model=UserOut)
async def signup_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Public signup endpoint. First user becomes superuser automatically."""
    # #region agent log
    import json
    with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"auth.py:32","message":"signup_user entry","data":{"password_len_chars":len(payload.password),"password_len_bytes":len(payload.password.encode('utf-8')),"email":payload.email[:10]+"..."},"timestamp":1733456789000})+'\n')
    # #endregion
    existing = await get_user_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    
    # Check if this is the first user (make them superuser)
    result = await db.execute(select(User))
    users = result.scalars().all()
    is_first_user = len(users) == 0
    
    # #region agent log
    with open('/Users/shivanshmahajan/Developer/workflowz_ai/.cursor/debug.log', 'a') as f:
        f.write(json.dumps({"sessionId":"debug-session","runId":"run1","hypothesisId":"A","location":"auth.py:50","message":"before create_user","data":{"password_len_chars":len(payload.password),"password_len_bytes":len(payload.password.encode('utf-8'))},"timestamp":1733456789001})+'\n')
    # #endregion
    user = await create_user(db, payload.email, payload.password, is_superuser=is_first_user)
    return UserOut.model_validate(user)


@router.post("/register", response_model=UserOut)
async def register_user(
    payload: UserCreate,
    _: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """Superuser-only endpoint for creating users."""
    existing = await get_user_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    user = await create_user(db, payload.email, payload.password, payload.is_superuser)
    return UserOut.model_validate(user)
