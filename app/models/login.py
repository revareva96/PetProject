from pydantic import Field

from app.models.common_model import SuccessResponseParams as _SuccessResponseParams

from .model import Model


class SuccessResponseParams(_SuccessResponseParams):
    """
    '200':
        description: Successful operation. Return status "success".
    """
    jwt: str = Field(
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.'
        'eyJ1c2VybmFtZSI6InN0cmluZyIsImxhc3RfbG9naW4iOiIyMDIyLTEyLTI2IDE3OjA3OjU3LjAzMTc1MiJ9.'
        'WsDWYLAcnW5VMSYuehGuyya8k_UgohDn10vNHI7itpI',
        description='Токен',
    )


class RequestObject(Model):
    param: int = Field()


class LoginPostRequestParams(Model):
    """
    tags:
    - Login
    produces:
    - application/json
    requestBody:
      description: This end-point allow to log in to the personal account.
      required: true
    """
    # examples: Optional[List[RequestObject]] = Field()
    login_or_email: str = Field(description='Логин пользователя')
    password: str = Field(description='Пароль пользователя')  # , include=[int])
