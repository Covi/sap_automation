# Fichero: core/protocols/__init__.py
from .file_handler_protocol import FileHandlerProtocol
from .print_service_protocol import PrintServiceProtocol

__all__ = [
    "FileHandlerProtocol", 
    "PrintServiceProtocol"
]