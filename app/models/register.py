from typing import Optional

from pydantic import Field

from .model import Model


class RegisterPostRequestParams(Model):
    """
    tags:
    - Personal account
    produces:
    - application/json
    requestBody:
      description: This end-point allow to create the personal account.
      required: true
    """
    mail: str = Field(description='Почтовый ящик пользователя')
    name: str = Field(description='Имя пользователя')
    patronymic: Optional[str] = Field(description='Отчество пользователя')
    login: str = Field(description='Отчество пользователя')
    telephone: Optional[str] = Field(description='Телефон пользователя')
    region: Optional[str] = Field(description='Регион пользователя')
    password: str = Field(description='Пароль пользователя')
