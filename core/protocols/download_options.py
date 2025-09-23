# core/protocols/download_options.py

from pathlib import Path
from .execution_options import Protocol, ExecutionOptions


class DownloadOptions(ExecutionOptions, Protocol):
    """
    Extiende ExecutionOptions con las opciones necesarias
    para transacciones que soportan exportación o descargas.
    """
    output_path: Path
    output_filename: str
