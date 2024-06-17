import bcrypt
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import async_session_factory
from database.models import User, Client, Status

fake = Faker('ru_RU')


async def create_fake_user(session: AsyncSession):
    full_name = fake.name()
    login = fake.user_name()
    password = fake.password()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(f'Создание пользователя: {full_name}\nЛогин: {login}\nПароль: {password}')
    user = User(
        full_name=full_name,
        login=login,
        password=hashed_password.decode('utf-8')
    )
    print(f"Пользователь создан: {user.full_name}")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_fake_client(session: AsyncSession, user: User):
    client = Client(
        account_number=fake.unique.random_int(min=100000, max=999999),
        last_name=fake.last_name(),
        first_name=fake.first_name(),
        middle_name=fake.middle_name(),
        birth_date=fake.date_of_birth(minimum_age=18, maximum_age=90),
        inn=fake.unique.numerify(text='##########'),
        responsible_person_id=user.id,
        status=Status.NOT_IN_WORK
    )
    print(f"Клиент создан для пользователя {user.full_name}")
    session.add(client)
    await session.commit()


async def create_fake_data():
    async with async_session_factory() as session:
        for _ in range(5):  # Создаем 5 пользователей
            user = await create_fake_user(session)
            for _ in range(10):  # Каждый пользователь имеет 10 клиентов
                await create_fake_client(session, user)


async def create_minimal_data():
    async with async_session_factory() as session:
        print("Создание одного пользователя")
        user = await create_fake_user(session)
