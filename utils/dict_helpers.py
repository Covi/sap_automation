# core/utils/dict_helpers.py

import types

def to_dot_notation(d: dict) -> types.SimpleNamespace:
    """
    Toma un diccionario y lo convierte en un objeto para acceder
    a sus claves con la notación de punto (ej: config.general.timeout).
    Funciona de forma recursiva para diccionarios anidados.
    """
    for key, value in d.items():
        if isinstance(value, dict):
            d[key] = to_dot_notation(value)
    return types.SimpleNamespace(**d)