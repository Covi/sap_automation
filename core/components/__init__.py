# core/components/__init__.py

"""
Módulo público de componentes SAP.

Aquí se exponen únicamente los componentes y abstracciones principales.
Las estrategias concretas permanecen en el submódulo `sap_form_strategies`.
"""

# Exponemos solo la abstracción base de estrategias (si existe)
from .form.sap_form_strategies import FormFillingStrategy, SimpleFillStrategy, RangeFillStrategy
from .form.sap_form_component import SAPFormComponent

from .menu.sap_menu_component import SAPMenuComponent
from .dialog.sap_export_dialog import SAPExportDialog
from .dialog.sap_menu_export_dialog import SAPMenuExportDialog

__all__ = [
    "SAPFormComponent",
    "SAPMenuComponent",
	"SAPExportDialog", 
    "SAPMenuExportDialog",
    "FormFillingStrategy", # contrato para todas las estrategias
    "SimpleFillStrategy",  # estrategia por defecto (sencilla)
	"RangeFillStrategy"    # estrategia para rangos
]
