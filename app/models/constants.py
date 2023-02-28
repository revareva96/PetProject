from typing import Type

from .check_uuid import CheckUUIDGetRequestParams
from .confirm import ConfirmPostRequestParams
from .login import LoginPostRequestParams
from .recover import RecoverPostRequestParams
from .register import RegisterPostRequestParams
from .store import StoreGetRequestParams


class GetRequestModels:
    store: Type[StoreGetRequestParams] = StoreGetRequestParams
    check_uuid: Type[CheckUUIDGetRequestParams] = CheckUUIDGetRequestParams


class PostRequestModels:
    login: Type[LoginPostRequestParams] = LoginPostRequestParams
    register: Type[RegisterPostRequestParams] = RegisterPostRequestParams
    confirm: Type[ConfirmPostRequestParams] = ConfirmPostRequestParams
    recover: Type[RecoverPostRequestParams] = RecoverPostRequestParams
