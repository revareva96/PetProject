from datetime import datetime, timedelta
from typing import Type, Union

import pytz
from aiohttp.web import Response, json_response
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from app.database.base import get_session
from app.database.models import ConfirmRegistration, RecoverPassword
from app.models.check_uuid import CheckUUIDGetRequestParams
from app.models.common_model import ErrorResponseParams, SuccessResponseParams

from ..config.config import get_settings
from .view import View

settings = get_settings()
utc = pytz.UTC
messages = {
    'confirm': 'Регистрация уже была подтверждена.',
    'recover': 'Ссылка недействительна.',
}


class CheckUUIDView(View):
    _get = {
        'request': CheckUUIDGetRequestParams,
        'responses': [SuccessResponseParams, ErrorResponseParams],
    }

    async def get(self) -> Response:
        income_model: CheckUUIDGetRequestParams = self.request.model
        session = await get_session()
        check_uuid = income_model.confirm if income_model.confirm else income_model.recover
        table: Union[Type[ConfirmRegistration], Type[RecoverPassword]] = ConfirmRegistration \
            if income_model.confirm else RecoverPassword
        delta = settings.confirm_registration_duration if income_model.confirm else settings.confirm_recover_duration
        results = await session.execute(
            select(table).filter(
                table.uuid == check_uuid,
            ),
        )
        results_scalars = results.scalars().first()
        # было подтверждение
        if results_scalars and results_scalars.confirm:
            await session.close()
            return json_response(
                ErrorResponseParams(
                    **{
                        'type': 'was verified',
                        'message': messages['confirm'] if table is ConfirmRegistration else messages['recover'],
                    },
                ).save(), status=400,
            )
        # сравниваем на наличие переменной и просрочкой времени подтверждения
        if not results_scalars or results_scalars.confirm_time < utc.localize(
                datetime.utcnow() - timedelta(
                    days=delta,
                ),
        ):
            await session.close()
            return json_response(
                ErrorResponseParams(
                    **{
                        'type': 'bad request',
                        'message': 'Ссылка недействительна.',
                    },
                ).save(), status=400,
            )
        try:
            # обновляем только подтверждение регистрации, так как смена пароля требует доп действий
            if table is ConfirmRegistration:
                await session.execute(
                    update(table).where(
                        table.uuid == check_uuid,
                    ).values(
                        confirm=True,
                    ),
                )
                await session.commit()
        except IntegrityError as e:
            raise e
        return json_response(SuccessResponseParams().save())
