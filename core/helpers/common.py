# -*- coding: utf-8 -*-

"""
Common useful helpers
"""


def is_local_file(path):
    """
    Check that specified path is local, not URL.
    """
    if path.lower().startswith("http://"):
        return False
    if path.lower().startswith("https://"):
        return False
    if path.lower().startswith("ftp://"):
        return False

    return True


def object_attrs_to_dict(obj: object, attrs: list) -> dict:
    """
    Returns dict with keys specified in 'attr' with values from 'obj' object.
    Example: object_attrs_to_dict(obj, ['a', 'b']) -> {'a': 'a value', 'b': 'b value'}
    """
    result = {}
    for attr in attrs:
        result[attr] = obj.__dict__[attr]
    return result


def str_list_to_dict(pairs_list):
    """
    Parses strings from list formatted as 'k1=v1' to dict with keys 'k1', 'v1'.
    Example: str_list_to_dict(['k=v', 'a=b']) —> {'k':'v', 'a': 'b'}
    :param pairs_list: list of strings
    :return: dict with parsed keys/values
    """
    result = {}
    for l in pairs_list:
        ar = l.split("=")
        result[ar[0]] = ar[1]

    return result


def search_dict_in_list_by_attr(items: list, attr_name, attr_value):
    for item in items:
        if item.get(attr_name) == attr_value:
            return item
    return None
