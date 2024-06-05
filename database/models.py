from sqlalchemy import Integer, String, Date, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from enum import Enum as PyEnum


class Status(PyEnum):
    NOT_IN_WORK = "Не в работе"
    IN_WORK = "В работе"
    DENIED = "Отказ"
    DEAL_CLOSED = "Сделка закрыта"


class Base(DeclarativeBase):
    pass


class Client(Base):
    __tablename__ = 'client'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    account_number: Mapped[int] = mapped_column(Integer, unique=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    responsible_person_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    status: Mapped[Status] = mapped_column(Text, nullable=False, default=Status.NOT_IN_WORK)

    responsible_user: Mapped['User'] = relationship('User', backref='clients')


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    login: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)


