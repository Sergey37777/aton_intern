from fastapi import FastAPI, Depends, HTTPException, Request, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from auth.auth_router import router, get_username
from database.models import Client, User, Base
from database.engine import get_async_session, engine


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

    print("База данных была пересоздана.")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, token=Depends(get_username)):
    return templates.TemplateResponse(
        request=request, name="base.html", context={'id': id, 'token': token}
    )


@app.get("/clients")
async def say_hello(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Client)
    result = await session.execute(stmt)
    result = result.scalars().all()
    return {"message": result}
