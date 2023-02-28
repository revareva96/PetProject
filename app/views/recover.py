import hashlib

from aiohttp.web import Response, json_response
from sqlalchemy import select, update

from app.config.config import get_settings
from app.database.base import get_session
from app.database.models import Passwords, RecoverPassword
from app.models.common_model import ErrorResponseParams, SuccessResponseParams, UnauthorizedResponseParams
from app.models.recover import RecoverPostRequestParams

from .view import View

settings = get_settings()


class RecoverView(View):
    _post = {
        'request': RecoverPostRequestParams,
        'responses': [SuccessResponseParams, ErrorResponseParams, UnauthorizedResponseParams],
    }

    async def post(self) -> Response:
        income_model: RecoverPostRequestParams = self.request.model
        uid = income_model.uuid
        try:
            session = await get_session()
            salt, number_iteration = settings.salt, settings.hash_iterations
            password = hashlib.pbkdf2_hmac(
                'sha256',
                income_model.password.encode('utf-8'),
                bytes(salt, encoding='utf8'),
                number_iteration,
            )
            results = await session.execute(
                select(RecoverPassword).filter(
                    RecoverPassword.uuid == uid,
                ),
            )
            idd = results.scalars().first().id
            # обновляем пароль
            await session.execute(
                update(Passwords).where(
                    Passwords.id == idd,
                ).values(
                    password=str(password),
                ),
            )
            # обновляем поле подтверждения в таблице с восстановлением пароля по uuid
            await session.execute(
                update(RecoverPassword).where(
                    RecoverPassword.id == idd,
                ).values(
                    confirm=True,
                ),
            )
            await session.commit()
        except Exception as e:
            raise e
        return json_response(
            SuccessResponseParams().save(),
        )
