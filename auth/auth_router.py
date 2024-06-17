from fastapi import APIRouter, Depends, HTTPException, Response, Request, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import timedelta, datetime
import bcrypt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from database.engine import get_async_session
from database.models import User
from config import SECRET_KEY

# Секретный ключ для создания JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token")
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                                 session: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.login}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True,
                        expires=access_token_expires.seconds)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post('/logout')
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Successfully Logged out"}


# Функция для аутентификации пользователя (замените на вашу реализацию)
async def authenticate_user(username: str, password: str, session: AsyncSession):
    # Здесь должна быть проверка пользователя с использованием базы данных
    stmt = select(User).filter(User.login == username)
    user = await session.execute(stmt)
    user = user.scalars().first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return user
    return None  # Замените на реальную проверку


async def get_current_user(request: Request, session: AsyncSession = Depends(get_async_session)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    stmt = select(User).where(User.login == username)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def get_username(request: Request, response: Response, session: AsyncSession = Depends(get_async_session)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        stmt = select(User).where(User.login == username)
        result = await session.execute(stmt)
        user = result.scalars().first()
        if user is None:
            return None
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    return username


@router.post('/signup')
async def signup(full_name: str = Form(...), username: str = Form(...), password: str = Form(...),
                 password_confirm: str = Form(...),
                 session: AsyncSession = Depends(get_async_session)):
    if password != password_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    stmt = select(User).where(User.login == username)
    result = await session.execute(stmt)
    user = result.scalars().first()
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(full_name=full_name, login=username, password=hashed_password.decode('utf-8'))
    session.add(new_user)
    await session.commit()
    return {"message": "User created successfully"}


@router.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "username": current_user.login}
