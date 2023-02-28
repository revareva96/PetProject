from typing import Optional

from pydantic import Field

from .model import Model

"""
Для моделей ответов (*ResponseParams) принцип создания docstring:
- первым параметром обязательно должен идти статус ответа(!);
- далее смещение по правилам синтаксиса yaml описание и любые дополнительные параметры.
Подробнее - https://swagger.io/docs/specification/describing-responses/
"""


class SuccessResponseParams(Model):
    """
    '200':
      description: Successful operation. Return status "success".
    """
    status: str = Field('Success', description='Успешный ответ')


class ErrorResponseParams(Model):
    """
    '400':
      description: Error operation. Return type of error and message.
    """
    type: Optional[str] = Field(description='Тип ошибки')
    message: Optional[str] = Field(description='Сообщение об ошибке')


class UnauthorizedResponseParams(Model):
    """
    '401':
      description: Unauthorized operation. Return type of error and message.
    """
    type: str = Field(description='Тип ошибки')
    message: str = Field(description='Сообщение об ошибке')


# TODO Перенести в README.md
"""
Для моделей POST запросов (*PostRequestParams) принцип создания docstring:
 - первыми параметрами могут идти опциональные (tags/produces и тд.);
 - но обязательно должен присутствовать параметр requestBody, для которого можно 
  уже добавить опциональные параметры (description, required и тд.)
Пример:
tags:
- Login
produces:
- application/json
requestBody:
  description: This end-point allow to log in to the personal account.
  required: true
Подробнее - https://swagger.io/docs/specification/describing-request-body/
"""

"""
Для моделей GET запросов (*GetRequestParams) принцип создания docstring:
    - первыми параметрами могут идти опциональные (tags, description и тд.), 
  остальное берется и агрегируются с помощью соответствующей модели.
Пример:
tags:
- Store
description: This end-point allows to get products from store by filter.
Подробнее - https://swagger.io/docs/specification/describing-parameters/
"""
