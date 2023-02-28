import json
import re
import uuid
from typing import Any, Callable, Dict, Optional

from aiohttp import web
from pydantic import ValidationError

from app.logger.logger import get_logger
from app.middlewares.constants import status_codes
from app.middlewares.utils import convert_duplicate_values_to_list
from app.models.common_model import ErrorResponseParams
from app.models.constants import GetRequestModels, PostRequestModels
from app.views.view import Request

logger = get_logger(__name__)

GET_INITIAL_PATH_REGEX = re.compile(r'/[a-zA-Z_]*')


class CustomMiddleware:

    def __init__(self):
        self.from_method_dispatcher = {
            'POST': self._post_request_validate_params,
            'GET': self._get_request_validate_params,
        }

    async def _to_validate_dispatcher(self, request: Request) -> None:
        if self.from_method_dispatcher.get(request.method):
            await self.from_method_dispatcher[request.method](request)

    @staticmethod
    def _error_response(e: Exception, typ: Optional[str] = None, msg: Optional[str] = None) -> Dict[str, Any]:
        data = {
            'type': typ if typ else str(type(e)),
            'message': msg if msg else str(e),
        }
        return {
            'status': e.status,
            'data': ErrorResponseParams.load(data).save(),
        }

    @staticmethod
    async def _get_request_validate_params(request: Request) -> None:
        first_regex = GET_INITIAL_PATH_REGEX.search(request.path)
        if not first_regex:
            return
        first_path = first_regex.group()[1:]
        validate_model = getattr(GetRequestModels, first_path, None)
        if validate_model:
            try:
                query_params = convert_duplicate_values_to_list(request.query, validate_model)
                logger.info('Validate params', request=request, request_params=query_params)
                request.model = validate_model.load(query_params)
            except ValidationError as e:
                e.status = 400
                raise e

    @staticmethod
    async def _post_request_validate_params(request: Request) -> None:
        first_regex = GET_INITIAL_PATH_REGEX.search(request.path)
        if not first_regex:
            return
        first_path = first_regex.group()[1:]
        validate_model = getattr(PostRequestModels, first_path, None)
        if validate_model:
            try:
                params = await request.json()
                logger.info('Validate params', request=request, request_params=params)
                request.model = validate_model.load(params)
            except ValidationError as e:
                e.status = 400
                raise e

    @web.middleware
    async def middleware(self, request: Request, handler: Callable) -> web.Response:
        try:
            request_id = uuid.uuid4()
            request.request_id = request_id
            logger.info('Get request', request=request)
            await self._to_validate_dispatcher(request)
            resp = await handler(request)
        except Exception as e:
            if not getattr(e, 'status', None):
                e.status = 500
            params_exception = self._error_response(e, *status_codes[e.status])
            message = 'Get internal error' if e.status == 500 else 'Get user exception'
            logger.error(message, request=request, response_params=params_exception) if e.status == 500 \
                else logger.info(message, request=request, response_params=params_exception)

            return web.json_response(**params_exception)
        if resp.headers['Content-type'][:16] == 'application/json':
            logger.info(
                'Success response', request=request,
                response_params=json.loads(resp.text),
            )
        return resp
