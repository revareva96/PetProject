import datetime
import uuid
from typing import Type, Union

from aiohttp.web import Response, json_response
from sqlalchemy import or_, select, update

from app.database.base import get_session
from app.database.models import ConfirmRegistration, RecoverPassword, Users
from app.models.common_model import ErrorResponseParams, SuccessResponseParams
from app.models.confirm import ConfirmPostRequestParams
from app.views.utils import send_message_in_thread

from .view import View


class ConfirmView(View):
    _post = {
        'request': ConfirmPostRequestParams,
        'responses': [SuccessResponseParams, ErrorResponseParams],
    }

    async def post(self) -> Response:
        income_model: ConfirmPostRequestParams = self.request.model
        login_or_email = income_model.login_or_email
        typ = income_model.type
        table: Union[Type[ConfirmRegistration], Type[RecoverPassword]] = RecoverPassword \
            if typ == 'recover' else ConfirmRegistration
        try:
            session = await get_session()
            results = await session.execute(
                select(Users).filter(
                    or_(
                        Users.login == login_or_email,
                        Users.mail == login_or_email,
                    ),
                ),
            )
            results_scalars = results.scalars().first()
            # проверяем, что пользователь найден по логину или почте
            if not results_scalars:
                return json_response(
                    ErrorResponseParams(
                        **{
                            'type': 'bad request',
                            'message': 'Пользователь не найден.',
                        },
                    ).save(), status=400,
                )
            idd, email = results_scalars.id, results_scalars.mail
            results_uuid = await session.execute(
                select(table).filter(
                    table.id == idd,
                ),
            )
            results_uuid_scalars = results_uuid.scalars().first()
            uid = uuid.uuid4()
            # если найден uuid пользователя, то обновляем статус подтверждения
            if results_uuid_scalars:
                if table is ConfirmRegistration and results_uuid_scalars.confirm:
                    return json_response(
                        ErrorResponseParams(
                            **{
                                'type': 'bad request',
                                'message': 'Пользователь уже подтвердил регистрацию.',
                            },
                        ).save(), status=400,
                    )
                await session.execute(
                    update(table).where(
                        table.id == idd,
                    ).values(
                        uuid=uid,
                        confirm_time=datetime.datetime.utcnow(),
                        confirm=False,
                    ),
                )
            # иначе вставляем новое поле
            else:
                session.add(
                    table(
                        id=idd,
                        uuid=uid,
                    ),
                )
            send_message_in_thread(
                email,
                typ,
                uid,
            )
            await session.commit()
        except Exception as e:
            raise e
        return json_response(SuccessResponseParams().save())
