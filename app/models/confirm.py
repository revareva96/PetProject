from typing import List

from pydantic import Field, ValidationError, validator

from .model import Model


class ConfirmPostRequestParams(Model):
    """
    tags:
    - Personal account
    produces:
    - application/json
    requestBody:
      description: This end-point allow to recover the password or to repeat confirm registration.
      required: true
    """
    login_or_email: str = Field(
        description='Логин или почтовый ящик',
    )
    type: str = Field(description='Тип подтверждения')

    @validator('type')
    def check_type_values(cls, v: List[str]) -> List[str]:
        if v not in ['recover', 'confirm']:
            raise ValidationError
        return v
