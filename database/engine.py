from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME

# Создаем асинхронный движок для подключения к базе данных
engine = create_async_engine(
    f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    echo=True
)

# Создаем фабрику асинхронных сессий
async_session_factory = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


# Функция для получения асинхронной сессии
async def get_async_session() -> AsyncSession:
    async with async_session_factory() as session:  # Используем async_session_factory
        yield session
