# pages/sap_report_page.py

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from .sap_page_base import SAPPageBase
from core.components.form.sap_form_component import SAPFormComponent
from core.components.form.sap_form_strategies import FormFillingStrategy

log = logging.getLogger(__name__)

class SAPReportPage(SAPPageBase, ABC):
    """
    Clase base abstracta para páginas SAP que siguen el patrón de un informe:
    1. Rellenar un formulario.
    2. Disparar un reporte.
    3. Esperar y procesar resultados (opcional según la página).

    Nota: Separamos la acción de ejecutar del paso de esperar resultados para
    respetar SRP y semántica.
    """

    def __init__(self, page, locator_provider: Any):
        super().__init__(page, locator_provider)

        # Componente para rellenar formularios
        self.form_component = SAPFormComponent(self)

        # La tabla de resultados es opcional; cada hija puede definirla
        self.results_table = None 

    # --- Propiedades abstractas obligatorias que deben definir las hijas ---
    @property
    @abstractmethod
    def form_locators(self) -> Dict[str, Any]:
        """Devuelve un diccionario de locators para los campos del formulario."""
        raise NotImplementedError

    @property
    @abstractmethod
    def fill_strategy(self) -> FormFillingStrategy:
        """Devuelve la estrategia de rellenado del formulario."""
        raise NotImplementedError

    # --- Método abstracto para esperar resultados, obligatorio solo para páginas de reporte ---
    @abstractmethod
    def esperar_resultados(self, timeout: int = 30000):
        """
        Cada página hija que tenga resultados debe implementar su lógica de espera.
        Esto queda público para ser llamado explícitamente por el flujo que lo necesite.
        """
        raise NotImplementedError

    # --- Métodos comunes de interacción ---
    def esperar_formulario(self, timeout: int = 30000) -> None:
        """
        Espera a que el formulario principal y los campos estén listos antes de rellenarlo.
        """
        try:
            self.form.wait_for(timeout=timeout)
            log.info("Formulario principal visible.")
        except Exception as e:
            log.error(f"Error esperando el formulario principal: {e}")
            raise

    def rellenar_formulario(self, payload: dict):
        """
        Rellena el formulario usando el componente y la estrategia definida por la hija.
        """
        self.form_component.fill_form(payload, self.form_locators, self.fill_strategy)

    # --- Método opcional legacy / alias ---
    def ejecutar(self):
        """
        Alias de 'execute()' para compatibilidad semántica.
        Solo dispara el botón ejecutar de SAP, no espera resultados.
        """
        log.info(f"Disparando reporte en la página {self.__class__.__name__} (alias de execute)")
        self.execute()

    # --- Legacy: esperar formulario antiguo, puede borrarse tras migración ---
    def esperar_formulario_legacy(self, timeout: int = 30000):
        """Esperar al formulario y a los campos específicos (legacy)."""
        self.wait_for_form(timeout=timeout)
        for locator in self.form_locators.values():
            self.page.wait_for_selector(locator[0], timeout=timeout)
