import hashlib
from datetime import datetime

import jwt
from aiohttp import web_exceptions
from aiohttp.web import Response, json_response
from sqlalchemy import or_, select, update

from app.config.config import get_settings
from app.database.base import get_session
from app.database.models import Passwords, Users
from app.models.common_model import ErrorResponseParams, UnauthorizedResponseParams
from app.models.login import LoginPostRequestParams, SuccessResponseParams

from .view import View

settings = get_settings()


class LoginView(View):
    _post = {
        'request': LoginPostRequestParams,
        'responses': [SuccessResponseParams, ErrorResponseParams, UnauthorizedResponseParams],
    }

    async def post(self) -> Response:
        income_model: LoginPostRequestParams = self.request.model
        try:
            session = await get_session()
            login_or_email = income_model.login_or_email
            result_password = await session.execute(
                select(Passwords).join(Users, Passwords.id == Users.id)
                .filter(
                    or_(
                        Users.login == login_or_email,
                        Users.mail == login_or_email,
                    ),
                ),
            )
            password = result_password.scalars().first().password
            salt, number_iteration = settings.salt, settings.hash_iterations
            password_for_check = hashlib.pbkdf2_hmac(
                'sha256',
                income_model.password.encode('utf-8'),
                bytes(salt, encoding='utf8'),
                number_iteration,
            )
            await session.execute(
                update(Users).where(
                    or_(
                        Users.login == login_or_email,
                        Users.mail == login_or_email,
                    ),
                ).values(
                    last_visit=datetime.utcnow(),
                ),
            )
            await session.commit()
            if password != str(password_for_check):
                raise web_exceptions.HTTPUnauthorized
        except AttributeError:
            raise web_exceptions.HTTPUnauthorized
        except Exception as e:
            raise e
        private_key = settings.private_key
        expired = str(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        token = jwt.encode(
            {
                'username': income_model.login_or_email,
                'expired': expired,
            },
            private_key,
            algorithm='HS256',
        )
        return json_response(
            SuccessResponseParams(jwt=token, status='Success').save(),
        )
