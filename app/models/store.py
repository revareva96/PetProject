from typing import List, Optional

from pydantic import Field

from .model import Model


class StoreGetRequestParams(Model):
    """
    tags:
    - Store
    description: This end-point allows to get products from store by filter.
    """
    product: List[str] = Field(description='Тип выбираемого товара')
    min_price: Optional[int] = Field(description='Минимальная цена товара')
    max_price: Optional[int] = Field(description='Максимальная цена товара')
