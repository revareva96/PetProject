import uuid as _uuid

from pydantic import Field

from .model import Model


class RecoverPostRequestParams(Model):
    """
    tags:
    - Personal account
    produces:
    - application/json
    requestBody:
      description: This end-point allow to log in to the personal account.
      required: true
    """
    uuid: _uuid.UUID = Field(description='UUID пользователя')
    password: str = Field(description='Пароль пользователя')
