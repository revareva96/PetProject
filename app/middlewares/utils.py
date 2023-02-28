from typing import Any, Dict

from multidict import MultiDictProxy

from app.models.model import Model


def convert_duplicate_values_to_list(query_dict: MultiDictProxy, model: Model) -> Dict[str, Any]:
    new_dict = {}
    # дублирующие имена должны быть представлены в виде списка
    duplicates_names = [name for name, model in model.__fields__.items() if 'List' in str(model)]

    for k in set(query_dict.keys()):
        k_values = query_dict.getall(k)
        if len(k_values) > 1 or k in duplicates_names:
            new_dict[k] = k_values
        else:
            new_dict[k] = k_values[0]
    return new_dict
