import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.config.config import Settings, get_settings
from app.database.base import Base

settings: Settings = get_settings()


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = {
        'schema': f'{settings.db_main_schema}',
    }

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    mail = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    login = Column(String, unique=True)
    telephone = Column(String, unique=True)
    region = Column(String)
    admin = Column(Boolean, default=False)
    last_visit = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)


class Passwords(Base):
    __tablename__ = 'users_passwords'
    __table_args__ = {
        'schema': f'{settings.db_main_schema}',
    }

    id = Column(Integer, ForeignKey(f'{settings.db_main_schema}.users.id', ondelete='CASCADE'), primary_key=True)
    password = Column(String)


class ConfirmRegistration(Base):
    __tablename__ = 'users_confirm_registration'
    __table_args__ = {
        'schema': f'{settings.db_main_schema}',
    }

    id = Column(Integer, ForeignKey(f'{settings.db_main_schema}.users.id', ondelete='CASCADE'), primary_key=True)
    uuid = Column(UUID(as_uuid=True))
    confirm_time = Column(DateTime(timezone=False), default=datetime.datetime.utcnow)
    confirm = Column(Boolean, default=False)


class RecoverPassword(Base):
    __tablename__ = 'users_recover_password'
    __table_args__ = {
        'schema': f'{settings.db_main_schema}',
    }

    id = Column(Integer, ForeignKey(f'{settings.db_main_schema}.users.id', ondelete='CASCADE'), primary_key=True)
    uuid = Column(UUID(as_uuid=True))
    confirm_time = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    confirm = Column(Boolean, default=False)
