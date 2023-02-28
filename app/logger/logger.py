import json
import logging
import logging.config
from typing import Any, Dict, MutableMapping, Optional, Tuple

from app.views.view import Request

logging.config.fileConfig('logging_config.ini')


class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg: str, kwargs: Dict[str, Any]) -> Tuple[str, MutableMapping[str, Any]]:
        request: Optional[Request] = kwargs.pop('request', self.extra['request'])
        request_params = kwargs.pop('request_params', self.extra['request_params'])
        response_params = kwargs.pop('response_params', self.extra['response_params'])
        request_id = request.request_id if request else None
        log_string = f'{msg}", "request_id": "{request_id}", '

        if response_params:
            return log_string + f'"response_json": {json.dumps(response_params, ensure_ascii=False)}', kwargs

        method = request.method if request else None
        log_string += f'"method": "{method}", '
        if request_params:
            return log_string + f'"params": {json.dumps(request_params, ensure_ascii=False)}', kwargs

        headers = json.dumps(dict(request.headers.items())) if request else None
        url = request.url if request else None
        return log_string + f'"url": "{url}", "headers": {headers}', kwargs


def get_logger(name: str) -> CustomAdapter:
    logger = CustomAdapter(logging.getLogger(name), {'request': None, 'request_params': None, 'response_params': None})
    return logger
