# core/protocols/execution_options.py

from typing import Protocol, Dict, Any

class ExecutionOptions(Protocol):
    """
    Opciones mínimas necesarias para ejecutar una transacción.
    Cubre únicamente los parámetros comunes a cualquier servicio.
    """
    params: Dict[str, Any]
