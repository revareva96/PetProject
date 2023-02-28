import uuid
from typing import Any, Dict, Optional

from pydantic import Field, ValidationError, root_validator

from .model import Model


class CheckUUIDGetRequestParams(Model):
    """
    tags:
    - Personal account
    description: This end-point allows to confirm registration or restore the password.
    """
    confirm: Optional[uuid.UUID] = Field(description='UUID для подтверждения регистрации')
    recover: Optional[uuid.UUID] = Field(description='UUID для восстановления пароля')

    @root_validator(pre=True)
    def check_exist_one_value(cls, v: dict) -> Dict[str, Any]:
        if not v:
            raise ValidationError
        not_values = list(v.keys())[0] not in list(cls.schema()['properties'].keys())
        if not_values or len(v) > 1:
            raise ValidationError
        return v
