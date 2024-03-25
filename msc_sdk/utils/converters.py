from datetime import datetime
from typing import List, Dict


def list_int_to_float(data_list: List[Dict], fields_to_convert: List[str]) -> List[Dict]:
    """
    Converts specified fields in a list from integers to floats with two decimal places precision.

    Args:
        data_list: A list containing the list data.
        fields_to_convert: A list of fields to convert to float.

    Returns:
        A list with specified fields converted to floats.
    """
    for item in data_list:
        for field_name in fields_to_convert:
            if field_name in item:
                item[field_name] = item[field_name] / 100

    return data_list


def list_float_to_int(data_list: List[Dict], fields_to_convert: List[str]) -> List[Dict]:
    """
    Converts specified fields in a list from floats to integers.

    Args:
        data_list: A list containing the list data.
        fields_to_convert: A list of fields to convert to integer.

    Returns:
        A list with specified fields converted to integers.
    """
    for item in data_list:
        for field_name in fields_to_convert:
            if field_name in item:
                item[field_name] = int(item[field_name] * 100)

    return data_list


def dict_int_to_float(model_dict: Dict, fields_to_convert: List[str]) -> Dict:
    """
    Converts specified fields in a dictionary from integers to floats with two decimal places precision.

    Args:
        model_dict: A dictionary containing the dict data.
        fields_to_convert: A list of fields to convert to float.

    Returns:
        A dictionary with specified fields converted to floats.
    """
    for field_name in fields_to_convert:
        if model_dict.get(field_name, None):
            model_dict[field_name] = model_dict[field_name] / 100
    return model_dict


def dict_float_to_int(model_dict: Dict, fields_to_convert: List[str]) -> Dict:
    """
    Converts specified fields in a dictionary from floats to integers.

    Args:
        model_dict: A dictionary containing the dict data.
        fields_to_convert: A list of fields to convert to integer.

    Returns:
        A dictionary with specified fields converted to integers.
    """
    for field_name in fields_to_convert:
        if field_name in model_dict:
            model_dict[field_name] = int(model_dict[field_name] * 100)

    return model_dict


def datetime_to_date_str(dt: datetime = datetime.now()) -> str:
    return dt.strftime("%Y-%m-%d")
