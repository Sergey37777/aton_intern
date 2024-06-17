from typing import List

from sqlalchemy import Integer, String, Date, Text, ForeignKey, DateTime, func, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from enum import Enum


class Status(str, Enum):
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
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[Date] = mapped_column(Date, nullable=False)
    inn: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    responsible_person_id: Mapped[int] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    status: Mapped[Status] = mapped_column(SQLEnum(Status), nullable=False, default=SQLEnum(Status.NOT_IN_WORK))

    responsible_user: Mapped['User'] = relationship('User', back_populates='clients')

    @property
    def status_display(self):
        return self.status.value


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    login: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)

    clients: Mapped[List['Client']] = relationship('Client', back_populates='responsible_user')
