import json
import uuid as _uuid
import warnings
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, cast

import yaml
from pydantic import BaseModel, Extra, ValidationError
from pydantic.class_validators import ROOT_KEY

ModelType = TypeVar('ModelType', bound='Model')


class UpgradeEnum(Enum):

    @classmethod
    def get_values(cls) -> List:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def get_dict(cls) -> Dict:
        d = {}
        [d.update({c.value: c.name}) for c in cls]
        return d


class BaseClasses(UpgradeEnum):
    # Базовые типы данных, которые сейчас есть для всех моделей Pydantic
    string = str
    integer = int
    uuid = _uuid.UUID


class Model(BaseModel):
    class Config:
        # Следует ли игнорировать (ignore), разрешать (allow) или
        # запрещать (forbid) дополнительные атрибуты во время инициализации
        # модели, подробнее:
        # https://pydantic-docs.helpmanual.io/usage/model_config/
        extra = Extra.ignore

    @classmethod
    def get_swagger_dict(cls, method: str, request: Optional[str] = None) -> Dict[str, Any]:
        # получение словаря из текущего docstring модели
        swagger_dict = yaml.load(cls.__doc__, Loader=yaml.Loader)
        # если это запрос, то генерим для него документацию в зависимости от метода
        if request:
            if method == 'post':
                content = swagger_dict['requestBody'].setdefault('content', {})
                application = content.setdefault('application/json', {})
                application['schema'] = cls.get_model_params_for_swagger()
            elif method == 'get':
                swagger_dict['parameters'] = cls.get_model_query_params_for_swagger()
        # иначе идем и генерим документацию ответов
        else:
            content = swagger_dict[list(swagger_dict.keys())[0]].setdefault('content', {})
            application = content.setdefault('application/json', {})
            application['schema'] = cls.get_model_params_for_swagger()
        return swagger_dict

    @classmethod
    def get_model_query_params_for_swagger(cls) -> List:
        list_params = []
        base_types = BaseClasses.get_dict()
        for name, model in cls.__fields__.items():
            if model.sub_fields:
                # todo выглядит костыльно, подумать, как получить тип, если он внешний по отношению к основному
                if 'List' in str(model.outer_type_):
                    schema = {
                        'schema': {
                            'type': 'array',
                            'items': {
                                'type': [base_types[model.type_]],
                            },
                        },
                    }
                # todo пока с выбором из нескольких полей не работает, надо подумать. Синтаксис для swagger не тот
                else:
                    schema = {
                        'schema': {
                            'oneOf': [base_types[m.type_] for m in model.sub_fields],
                        },
                    }
            else:
                schema = {
                    'schema': {
                        'type': base_types[model.type_]
                        if model.type_ is not _uuid.UUID else 'string',  # todo поправить
                    },
                }
            list_params.append(
                {
                    'in': 'query',
                    'name': name,
                    'required': True if model.required else False,
                    **schema,
                    'description': model.field_info.description if model.field_info.description else None,
                },
            )
        return list_params

    @classmethod
    def get_model_params_for_swagger(cls, dict_params: Dict = {}) -> Dict:
        params = {
            'type': 'object',
            'properties': {},
        }
        # если нет словаря, то первый вызов функции, иначе рекурсивно обходятся модели
        if not dict_params:
            dict_params = params
        base_types = BaseClasses.get_dict()
        for name, model in cls.__fields__.items():
            dict_name = dict_params['properties'].setdefault(f'{name}', {})
            # проверка, что тип данных является моделью, тогда рекурсивный вызов функции
            if issubclass(model.type_, Model):
                dict_name.update(params)
                model.type_.get_model_params_for_swagger(dict_name)
            # иначе просто обогащение словаря
            elif model.type_ in BaseClasses.get_values():
                if model.type_ in (str, _uuid.UUID):
                    dict_name['example'] = model.default if model.default else 'string'
                elif model.type_ == int:
                    dict_name['example'] = model.default if model.default else '100'
                dict_name['type'] = base_types[model.type_]
                dict_name['required'] = True if model.required else False
            else:
                e = ValidationError
                raise e
        return dict_params

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    @classmethod
    def load(cls, data: Union[Dict[str, Any], 'Model']) -> 'ModelType':
        return super().parse_obj(data)

    def save(
            self,
            *,
            include: Union[set, Dict] = None,
            exclude: Union[set, Dict] = None,
            by_alias: bool = True,
            skip_defaults: bool = None,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            save_properties: bool = False,
            encoder: Optional[Callable[[Any], Any]] = None,
            **dumps_kwargs: Any,
    ) -> Dict[str, Any]:
        """Конвертация объекта в словарь через сериализацию.

        Метод dict() рекурсивно превращает модели в словари, но оставляет прочие типы прежними.
        Например, UUID / Enum / datetime так ими и останутся, и не смогут сериализоваться в json.
        Есть ещё метод json(), он использует *кастомный* энкодер, сериализующий все эти типы и
        возвращающий строку.

        Данный метод по своей сути попирует функционал json, но с возможностью сериализовать свойства,
        а затем десериализует, чтобы получить структуру, состоящую из примитивных типов.
        """
        if skip_defaults is not None:
            warnings.warn(
                f'{self.__class__.__name__}.json(): "skip_defaults" is deprecated and replacedby "exclude_unset"',
                DeprecationWarning,
            )
            exclude_unset = skip_defaults

            encoder = cast(Callable[[Any], Any], encoder or self.json_encoder)

        # При save_properties = True в словарь также конвертируются и свойства
        data = self.dict(
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            # save_properties=save_properties,
        )

        if self.__custom_root_type__:
            data = data[ROOT_KEY]

        return json.loads(self.__config__.json_dumps(data, default=encoder, **dumps_kwargs))
