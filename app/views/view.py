import uuid

import yaml
from aiohttp.web import Request as _Request
from aiohttp.web import View as _View

from app.models.model import Model

tags_constants = {'CheckTokenView': 'Login'}


class Request(_Request):
    model: Model
    request_id: uuid.UUID


class View(_View):

    @property
    def request(self) -> Request:
        return super().request

    @classmethod
    def create_documentation(cls):
        # получение методов, которые есть для данного View
        method_list = [
            func for func in cls.__dict__.keys() if callable(getattr(cls, func)) and func in ('get', 'post')
        ]

        for method in method_list:
            # получение атрибута с моделями запросов/ответов
            models = getattr(cls, f'_{method}')
            swagger_dict = {}
            request_model = models.get('request')  # модель запроса
            if request_model:
                # обогащение документации модели запроса
                swagger_dict = request_model.get_swagger_dict(method, 'request')
            responses_models = models.get('responses')  # модели ответов
            if responses_models:
                # обогащение документации моделями ответов
                responses = swagger_dict.setdefault('responses', {})
                for response_model in responses_models:
                    responses.update(response_model.get_swagger_dict(method))
            # получение текущего метода, для которого обогощается документация swagger
            method_doc = getattr(cls, method)
            if not swagger_dict.get('tags'):
                swagger_dict['tags'] = [tags_constants[cls.__name__]]
            # добавление docstring текущему методу + прочерки (без них не считается yaml формат)
            method_doc.__doc__ = '---\n' + yaml.dump(swagger_dict)
