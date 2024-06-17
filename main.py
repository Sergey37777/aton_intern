import asyncio

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from auth.auth_router import router, get_username
from database.models import Client, User, Base, Status
from database.engine import get_async_session, engine
from data_faker import create_fake_data, create_minimal_data

app = FastAPI()

app.include_router(router, prefix='/auth')
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Удалить все существующие таблицы
        await conn.run_sync(Base.metadata.drop_all)
        # Создать их заново
        await conn.run_sync(Base.metadata.create_all)
        # Создать фейковые данные
    await create_fake_data()

    print("База данных была пересоздана.")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, token=Depends(get_username), session=Depends(get_async_session)):
    if token:
        # stmt = select(User).options(selectinload(User.clients)).where(User.login == token)
        stmt = select(User).where(User.login == token)
        result = await session.execute(stmt)
        user = result.scalars().first()
        stmt = select(Client).where(Client.responsible_person_id == user.id)
        result = await session.execute(stmt)
        clients = result.scalars().all()
    else:
        clients = []
    return templates.TemplateResponse(
        request=request, name="base.html", context={'id': id, 'token': token, 'clients': clients, 'Status': Status}
    )


@app.get("/clients")
async def say_hello(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Client)
    result = await session.execute(stmt)
    result = result.scalars().all()
    return {"message": result}


@app.post("/update-status")
async def update_status(
        client_id: int = Form(...),
        status: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Client).filter_by(id=client_id))
    client = result.scalars().first()
    if client:
        client.status = Status[status]
        await session.commit()
    return RedirectResponse(url="/", status_code=303)
