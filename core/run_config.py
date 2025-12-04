# core/run_config.py

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class RunConfig:
    """
    DTO que define el contrato de configuración para una ejecución.
    Es agnóstico a si viene de CLI, GUI o API.
    """
    transaction_name: str
    params: Dict[str, Any]
    browser: str
    headless: bool
    log_level: Optional[str]
    download_dir: Optional[str]
    persistent_session: bool = False
    wait_after_results: bool = False