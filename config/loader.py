# config/loader.py

import os
import toml
from pathlib import Path
from dotenv import load_dotenv
from platformdirs import user_downloads_path
from pydantic import ValidationError

from .settings import GlobalConfig

class ConfigLoader:
    def __init__(self, toml_path: Path, env_path: Path):
        self.toml_path = toml_path
        self.env_path = env_path

    def _load_secrets(self) -> dict:
        load_dotenv(self.env_path)
        user = os.getenv("SAP_USER")
        password = os.getenv("SAP_PASSWORD")
        if not user or not password:
            raise EnvironmentError("Faltan credenciales SAP_USER o SAP_PASSWORD.")
        return {"sap_username": user, "sap_password": password}

    def _resolve_download_dir(self, configured_path: str | None) -> Path:
        if configured_path:
            return Path(configured_path)
        return user_downloads_path()

    def load(self) -> GlobalConfig:
        if not self.toml_path.exists():
            raise FileNotFoundError(f"Config no encontrada: {self.toml_path}")
            
        with open(self.toml_path, "r", encoding="utf-8") as f:
            raw_data = toml.load(f)

        secrets = self._load_secrets()

        # --- Lógica de Inyección de Dependencias (Rutas) ---
        
        # 1. Resolver ruta global
        general_data = raw_data.get("general", {})
        global_download_dir = self._resolve_download_dir(general_data.get("download_dir"))
        general_data["download_dir"] = global_download_dir
        
        # 2. Inyectar ruta global en cada transacción ESPECÍFICA
        #    Iteramos sobre el diccionario de transacciones del TOML
        transactions_data = raw_data.get("transactions", {})
        
        for key, tx_data in transactions_data.items():
            # Si la transacción específica no tiene ruta, le ponemos la global
            if "download_dir" not in tx_data:
                tx_data["download_dir"] = global_download_dir

        # 3. Construcción del diccionario final para Pydantic
        merged_data = {
            "general": general_data,
            "logging": raw_data.get("logging"),
            "transactions": transactions_data, # Pydantic mapeará mb52 -> Mb52Config, etc.
            **secrets
        }

        try:
            return GlobalConfig(**merged_data)
        except ValidationError as e:
            raise ValueError(f"Error de validación en la configuración: {e}")