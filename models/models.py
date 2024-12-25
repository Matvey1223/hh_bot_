from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from datetime import datetime
from sqlalchemy.types import TIMESTAMP

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column()
    text: Mapped[str] = mapped_column(nullable=True)
    salary: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    shedule: Mapped[str] = mapped_column(nullable=True)
    experience: Mapped[str] = mapped_column(nullable=True)
    prof_roles: Mapped[str] = mapped_column(nullable=True)
    test: Mapped[str] = mapped_column(nullable=True)
    new_vacancies_notification: Mapped[bool] = mapped_column(default=False)
    freq_new_vacancy_notifications: Mapped[int] = mapped_column(default = 12)
    freq_views_resume: Mapped[int] = mapped_column(default=12)
    token: Mapped[str] = mapped_column(nullable=True)
    monitoring_resume_interval: Mapped[int] = mapped_column(default=8)


class UserVacancies(Base):
    __tablename__ = 'user_vacancies'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column()
    name: Mapped[str] = mapped_column()
    salary: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    schedule: Mapped[str] = mapped_column()
    experience: Mapped[str] = mapped_column()
    employment: Mapped[str] = mapped_column()
    test: Mapped[bool] = mapped_column()
    prof_role: Mapped[str] = mapped_column()
    url: Mapped[str] = mapped_column()
    company: Mapped[str] = mapped_column()

class FilterLogs(Base):
    __tablename__ = 'filter_logs'
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column()
    text: Mapped[str] = mapped_column()
    salary: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    schedule: Mapped[str] = mapped_column()
    experience: Mapped[str] = mapped_column()
    test: Mapped[bool] = mapped_column()
    prof_role: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(type_=TIMESTAMP(timezone=True))
    for_notifications: Mapped[bool] = mapped_column(default=False)

class UserResumes(Base):
    __tablename__ = 'user_resumes'
    user_id: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column()
    resume_id: Mapped[str] = mapped_column(primary_key=True)
    autoupdate: Mapped[bool] = mapped_column(default=False)
    monitoring_views: Mapped[bool] = mapped_column(default=False)