from aiohttp import web

from app.models.common_model import ErrorResponseParams, SuccessResponseParams
from app.models.store import StoreGetRequestParams

from .view import View


class StoreView(View):
    _get = {
        'request': StoreGetRequestParams,
        'responses': [SuccessResponseParams, ErrorResponseParams],
    }

    async def get(self) -> web.Response:
        return web.json_response(SuccessResponseParams().save())
