from datetime import datetime, timedelta

import jwt
from aiohttp.web import Response, json_response
from aiohttp.web_exceptions import HTTPUnauthorized
from jwt.exceptions import DecodeError

from app.config.config import get_settings
from app.models.common_model import ErrorResponseParams, SuccessResponseParams

from .view import View

settings = get_settings()


class CheckTokenView(View):
    _get = {
        'responses': [SuccessResponseParams, ErrorResponseParams],
    }

    async def get(self) -> Response:
        token = self.request.headers.get('Authorization')
        if not token:
            raise HTTPUnauthorized
        token = token[6:]  # берем с 6 элемента, чтоб отсечь приставку Basic
        try:
            # если не передали токен
            if token == 'undefined':
                raise HTTPUnauthorized
            # выкинет ошибку DecodeError, если не пройдет проверку на сигнатуру
            token = jwt.decode(
                token,
                settings.private_key,
                algorithms=['HS256'],
            )
            expired = datetime.strptime(token['expired'], '%Y-%m-%d %H:%M:%S')
            # если просрочен
            if expired < datetime.utcnow() - timedelta(days=settings.lifetime_token_duration):
                raise HTTPUnauthorized
        except DecodeError:
            raise HTTPUnauthorized
        return json_response(SuccessResponseParams().save())
