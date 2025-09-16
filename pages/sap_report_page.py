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
    2. Ejecutar un reporte.
    3. Esperar y procesar una tabla de resultados.
    """
    def __init__(self, page, locator_provider: Any):
        super().__init__(page, locator_provider)
        self.form = SAPFormComponent(self)
        # La tabla de resultados es un concepto común, pero cada hijo 
        # debe definir e inicializar su locator o componente específico.
        self.results_table = None 

    @property
    @abstractmethod
    def form_locators(self) -> Dict[str, Any]:
        """
        Propiedad abstracta. Cada página hija DEBE implementar esto.
        Debe devolver el diccionario que mapea nombres de campo a locators de Playwright.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def fill_strategy(self) -> FormFillingStrategy:
        """
        Propiedad abstracta. Cada página hija DEBE devolver una instancia 
        de su estrategia de rellenado de formulario.
        """
        raise NotImplementedError

    @abstractmethod
    def _esperar_resultados(self, timeout: int = 30000):
        """
        Método abstracto. Cada página hija DEBE implementar su propia
        lógica de espera para los resultados tras una ejecución.
        """
        raise NotImplementedError

    def rellenar_formulario(self, payload: dict):
        """
        Método común para rellenar el formulario.
        Usa las propiedades 'form_locators' y 'fill_strategy' que la 
        clase hija está obligada a definir.
        """
        self.form.fill_form(payload, self.form_locators, self.fill_strategy)

    def ejecutar(self):
        """
        Método común para ejecutar el informe y esperar los resultados.
        Llama al método 'execute' de la clase base y luego a la lógica
        de espera específica de la clase hija.
        """
        log.info(f"Ejecutando reporte en la página {self.__class__.__name__}")
        self.execute()
        self._esperar_resultados()