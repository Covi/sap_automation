# builders/formatters.py

from datetime import date
from typing import Tuple, Optional, Callable

# --- Especialista en fechas ---
def format_date(value: date, formato: str) -> str:
    """
    Convierte un objeto date a string usando el formato indicado.

    Args:
        value (date): Objeto datetime.date a convertir.
        formato (str): Formato de salida para strftime.

    Returns:
        str: Fecha formateada.
    """
    return value.strftime(formato)


# --- Especialista en booleanos ---
def format_bool(value: bool) -> str:
    """
    Convierte un booleano a 'X' o ''.

    Args:
        value (bool): Valor booleano.

    Returns:
        str: 'X' si True, '' si False.
    """
    return 'X' if value else ''


# --- Especialista en tuplas (rangos) ---
def format_tuple(value: Tuple, date_formatter: Optional[Callable[[date], str]] = None) -> str:
    """
    Convierte una tupla de rango en un string separado por comas,
    aplicando formateo a cada elemento según sea necesario.

    Args:
        value (Tuple): Tupla de elementos.
        date_formatter (callable, optional): Función para formatear fechas.

    Returns:
        str: String con los elementos separados por coma.
    """
    parts = []
    for item in value:
        if item is None:
            parts.append("")
        elif isinstance(item, date) and date_formatter:
            parts.append(date_formatter(item))
        else:
            parts.append(str(item))
    
    return ",".join(parts)
