# pages/sap_report_page.py

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from .sap_page_base import SAPPageBase
from core.components.form.sap_form_component import SAPFormComponent
from core.components.form.sap_form_strategy_factory import SAPFormStrategyFactory

log = logging.getLogger(__name__)

class SAPReportPage(SAPPageBase, ABC):
    """
    Clase base abstracta para páginas SAP que siguen el patrón de un informe:
    1. Rellenar un formulario.
    2. Disparar un reporte.
    3. Esperar y procesar resultados (opcional según la página).
    """

    def __init__(self, page, locator_provider: Any):
        super().__init__(page, locator_provider)

        # Componente formulario, básico
        self.form_component = SAPFormComponent(self)

        # Componente tabla de resultados, opcional
        self.results_table = None

    # --- Propiedades abstractas obligatorias ---
    @property
    @abstractmethod
    def form_locators(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def esperar_resultados(self, timeout: int = 30000):
        raise NotImplementedError

    # --- Métodos comunes ---
    def esperar_formulario(self, timeout: int = 30000) -> None:
        try:
            self.form.wait_for(timeout=timeout)
            log.info("Formulario principal visible.")
        except Exception as e:
            log.error(f"Error esperando el formulario principal: {e}")
            raise

    def rellenar_formulario(self, payload: dict):
        """
        Delega el rellenado del formulario al componente especializado.
        """
        self.form_component.fill_form(payload, self.form_locators)

    def ejecutar(self):
        log.info(f"Ejecutando reporte en la página {self.__class__.__name__}")
        self.execute()  # Asumiendo que 'execute' hace el clic en el botón de ejecutar
