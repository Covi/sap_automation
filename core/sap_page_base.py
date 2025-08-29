# core/sap_page_base.py
# Clase base para todas las páginas SAP, con elementos y métodos comunes

import warnings
from playwright.sync_api import Page
from .page_base import PageBase
from .providers.base_provider import BaseLocatorProvider

class SAPPageBase(PageBase):
    """
    Una clase base para todas las páginas de SAP.
    Proporciona acceso y métodos para interactuar con elementos comunes de la UI de SAP.
    """
    def __init__(self, page: Page, locator_provider: BaseLocatorProvider):
        super().__init__(page)
        self._provider = locator_provider # Guardamos el provider para uso interno
        
        # --- Definimos los elementos comunes que toda página SAP tendrá ---
        self.status_bar = page.locator(self._provider.get('common.status_bar'))
        self.execute_button = page.locator(self._provider.get('common.ejecutar'))

    # --- Métodos de acción comunes ---
    
    def get_status_bar_text(self) -> str:
        """
        Espera a que la barra de estado tenga texto y lo devuelve.
        Esencial para verificar que una acción ha tenido éxito.
        """
        self.status_bar.wait_for(state="visible")
        return self.status_bar.inner_text()

    def accept(self):
        """
        Teclea Enter para aceptar diálogos o mensajes.
        """
        self.page.keyboard.press("Enter")

    def execute(self):
        """
        Hace clic en el botón 'Ejecutar' (F8) común.
        """
        self.execute_button.click()

    def _fill_form(self, form_locators_map: dict, form_data: object):
        """
        Método genérico que itera sobre un objeto de datos y rellena los campos
        de un formulario según un mapa de locators.
        """
        # itera sobre los campos del dataclass (ej. 'material', 'centro')
        warnings.warn(
            "El método _fill_form está obsoleto. Por favor, "
            "usa SAPFormComponent.fill_form en su lugar.",
            DeprecationWarning,
            stacklevel=2
        )

        for field_name, field_value in vars(form_data).items():
            # Si el campo tiene un valor y existe en nuestro mapa de locators
            if field_value is not None and field_name in form_locators_map:
                locator = form_locators_map[field_name]
                locator.fill(str(field_value))

    def pause(self):
        """
        Pausa la ejecución para inspección manual.
        Útil para debugging.
        """
        self.page.pause()