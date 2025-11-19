# pages/iq09_page.py

import logging
from typing import Any, Dict

from playwright.sync_api import Download, TimeoutError, Error

from .sap_report_page import SAPReportPage

# Componentes y Estrategias
from core.components.form.sap_form_strategies import SimpleFillStrategy, FormFillingStrategy
from core.components.menu.sap_menu_component import SAPMenuComponent
from core.components.table.sap_table_component import SAPTableComponent
from core.components.dialog.sap_menu_export_dialog import SAPMenuExportDialog

log = logging.getLogger(__name__)

class Iq09Page(SAPReportPage):
    """
    Page Object Model para la transacción IQ09 de SAP.
    Hereda la lógica común de informes de SAPReportPage.
    """
    def __init__(self, page, locator_provider: Any):
        super().__init__(page, locator_provider)

        # --- Definición de componentes y locators específicos de IQ09 ---
        self.menu = SAPMenuComponent(self)
        self.export_dialog = SAPMenuExportDialog(self)

        # Tabla de resultados:
        # "Dentro del div Raster Layout (RL), busca la tabla STCS"
        locator = "div[ct='RL'] >> table[ct='STCS']"
        #locator = "<input id="M0:46:1:1:1::0:32" ct="CBS" lsdata="{&quot;x&quot;:0,&quot;1&quot;:&quot;FREETEXT&quot;,&quot;3&quot;:&quot;M0:46:1:1:1::0:32_TALB&quot;,&quot;5&quot;:&quot;SE-Modificación&quot;,&quot;7&quot;:true,&quot;14&quot;:&quot;SERVER&quot;,&quot;17&quot;:false,&quot;20&quot;:false,&quot;21&quot;:{&quot;SID&quot;:&quot;wnd[0]/usr/subSUB_ALL:SAPLCOIH:3001/ssubSUB_LEVEL:SAPLCOIH:1100/subSUB_KOPF:SAPLCOIH:1102/txtCAUFVD-KTEXT&quot;,&quot;Type&quot;:&quot;GuiTextField&quot;,&quot;value&quot;:&quot;SE-Modificación&quot;,&quot;maxlen&quot;:40,&quot;focusable&quot;:&quot;X&quot;},&quot;22&quot;:&quot;pstxt&quot;}" lsevents="{&quot;Change&quot;:[{},{&quot;1&quot;:&quot;value&quot;,&quot;3&quot;:true,&quot;7&quot;:true}],&quot;Select&quot;:[{},{&quot;1&quot;:&quot;value&quot;,&quot;3&quot;:true,&quot;7&quot;:true}],&quot;Validate&quot;:[{},{}],&quot;DeleteItem&quot;:[{},{&quot;3&quot;:true}],&quot;ListAccess&quot;:[{&quot;ResponseData&quot;:&quot;delta&quot;,&quot;TransportMethod&quot;:&quot;full&quot;,&quot;EnqueueCardinality&quot;:&quot;none&quot;},{&quot;3&quot;:true,&quot;8&quot;:&quot;history&quot;,&quot;limitlen&quot;:&quot;X&quot;}],&quot;DoubleClick&quot;:[{},{&quot;1&quot;:&quot;action/2&quot;,&quot;2&quot;:true,&quot;3&quot;:true}],&quot;ClipboardTablePaste&quot;:[{},{&quot;0&quot;:&quot;GuiTextField&quot;,&quot;1&quot;:&quot;action/25&quot;,&quot;2&quot;:true,&quot;3&quot;:true}]}" data-cust-sid="Cvc5+0lu9HLMi3tKcVxang==" type="text" autocomplete="off" maxlength="40" tabindex="0" ti="0" title="Texto breve" class="lsField__input" value="SE-Modificación" role="textbox" name="InputField">"
        self._results_table_locator = self.playwright_page.locator(locator)
        self.table = SAPTableComponent(self, self._results_table_locator)


    # --- Implementación de las propiedades abstractas obligatorias ---
    @property
    def form_locators(self) -> Dict[str, Any]:
        """Provee el mapa de locators del formulario para la clase base."""
        return {
            'centro': self.playwright_page.locator(self._provider.get('form.centro')),
            'n_serie': self.playwright_page.locator(self._provider.get('form.n_serie')),
        }

    @property
    def fill_strategy(self) -> FormFillingStrategy:
        """Provee la estrategia de rellenado para la clase base."""
        return SimpleFillStrategy()

    # --- Implementación de los métodos abstractos obligatorios ---
    def esperar_resultados(self, timeout: int = 30000):
        """
        Implementa la lógica de espera específica de la transacción IQ09.
        En este caso, esperamos a que la tabla de resultados aparezca.
        """
        log.debug("Esperando la tabla de resultados de IQ09...")
        # Usamos el método is_visible del componente que ya gestiona esperas
        if not self.table.is_visible(timeout=timeout):
             # Si falla, el propio componente ya habrá logueado el warning,
             # pero aquí podemos lanzar el error de Playwright para que suba.
             raise TimeoutError("La tabla no apareció a tiempo.")

    # --- Métodos específicos de IQ09 que se mantienen ---
    def is_results_table_visible(self) -> bool:
        """Comprueba si la tabla de resultados del informe está visible."""
        return self.table.is_visible(timeout=1000) # Check rápido

    def descargar_informe(self) -> Download:
        """Inicia la descarga a través de la navegación por el menú de SAP."""
        log.info("Iniciando descarga para IQ09 a través del menú SAP...")
        try:
            self.menu.navigate_to("Menú", "Lista", "Grabar", "Fichero...")
            return self.export_dialog.exportar_como_spreadsheet()
        except (TimeoutError, Error) as e:
            log.error(f"El proceso de descarga para IQ09 ha fallado: {e}")
            raise