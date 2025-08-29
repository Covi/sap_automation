# Fichero: core/components/sap_menu_component.py

from playwright.sync_api import Page, Locator
from utils.logger import log

class SAPMenuComponent:
    """
    Gestiona la interacción con el menú de navegación superior estándar de SAP.
    Su única responsabilidad es navegar a través de una ruta de menú proporcionada.
    """
    def __init__(self, page: Page):
        self.page = page

    def _get_menu_item(self, text: str) -> Locator:
        """
        Localiza un elemento de menú por su texto, priorizando roles semánticos.
        """
        locator_con_rol = self.page.get_by_role("button", name=text, exact=True).or_(
                              self.page.get_by_role("menuitem", name=text, exact=True)
                          )
        
        # Se añade get_by_text como fallback por si SAP no renderiza el rol correcto.
        return locator_con_rol.or_(self.page.get_by_text(text, exact=True))

    def navigate_to(self, *path: str):
        """
        Navega a través de una secuencia de clics en el menú.

        Ejemplo: menu.navigate_to("Menú", "Fichero...")
        """
        log.info(f"Navegando por el menú: {' -> '.join(path)}")
        for item_text in path:
            menu_item = self._get_menu_item(item_text).first
            menu_item.click()

            # AÑADE ESTA LÍNEA PARA DEPURAR EL SIGUIENTE PASO
            # Esto pausará la ejecución justo después de cada clic en el menú.
            self.page.pause()