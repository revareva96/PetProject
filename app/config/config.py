from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    salt: str = 'very_difficult_secret'
    hash_iterations: int = 100000
    cors_host: str = 'http://localhost:3001'
    app_port: int = 5051
    db: str = 'cigar_db'
    db_user: str = 'cigar'
    db_password: str = 'cigar'
    db_host: str = 'localhost'
    db_port: int = 5433
    db_main_schema: str = 'data'
    private_key: str = 'secret'
    lifetime_token_duration: int = 7
    confirm_registration_duration: int = 7
    confirm_recover_duration: int = 1
    smtp_host: str = 'smtp.mail.ru'
    smtp_from: str = 'example@mail.ru'
    smtp_user: str = 'example@mail.ru'
    smtp_password: str = 'very_difficult_secret'
    smtp_port: int = 465


@lru_cache
def get_settings() -> 'Settings':
    return Settings()
