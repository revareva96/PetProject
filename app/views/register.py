import hashlib
import uuid

from aiohttp.web import Response, json_response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.config.config import get_settings
from app.database.base import get_session
from app.database.models import ConfirmRegistration, Passwords, Users
from app.models.register import RegisterPostRequestParams

from ..models.common_model import ErrorResponseParams, SuccessResponseParams
from .utils import send_message_in_thread
from .view import View

settings = get_settings()


class RegisterView(View):
    _post = {
        'request': RegisterPostRequestParams,
        'responses': [SuccessResponseParams, ErrorResponseParams],
    }

    async def post(self) -> Response:
        session = await get_session()
        income_model: RegisterPostRequestParams = self.request.model
        try:
            session.add(Users(**income_model.save(exclude={'password'})))
            user_results = await session.execute(select(Users).filter(Users.login == income_model.login))
            results = user_results.scalars().first()
            user_id = results.id
            user_email = results.mail
            salt, number_iteration = settings.salt, settings.hash_iterations
            password = hashlib.pbkdf2_hmac(
                'sha256',
                income_model.password.encode('utf-8'),
                bytes(salt, encoding='utf8'),
                number_iteration,
            )
            session.add(Passwords(id=user_id, password=str(password)))
            uid = uuid.uuid4()
            session.add(ConfirmRegistration(id=user_id, uuid=uid))
            send_message_in_thread(
                user_email, 'confirm', uid,
            )
            await session.commit()
        except IntegrityError:
            return json_response(
                ErrorResponseParams(
                    **{
                        'type': 'already exist',
                        'message': 'Пользователь с таким логином/почтовым ящиком уже существует.',
                    },
                ).save(), status=400,
            )
        except Exception as e:
            raise e
        return json_response(SuccessResponseParams().save())
