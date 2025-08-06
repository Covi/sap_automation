from core.browser_manager import BrowserManager
from utils.logger import log

# MB52
from core.builders.mb52 import build_mb52_service
from data_models.mb52_models import Mb52FormData
from config import Mb52Config

def main():
    """
    Función principal que ejecuta el robot de MB52.
    """
    log.info("Iniciando ejecución desde main.py")
    manager = BrowserManager(headless=True) # Lo ejecutamos en headless
    
    try:
        page = manager.start_browser()
        
        # 1. Usamos el builder para obtener el servicio ya logueado y listo
        mb52_service = build_mb52_service(page)
        
        # 2. Preparamos los datos para la tarea
        datos_informe = Mb52FormData(centro=Mb52Config.DEFAULT_CENTRO)
        fichero_de_salida = f"{Mb52Config.DOWNLOAD_DIR}/{Mb52Config.EXPORT_FILENAME}"
        
        # 3. Ejecutamos la lógica de negocio
        mb52_service.generar_y_descargar_informe_completo(
            form_data=datos_informe,
            nombre_fichero=fichero_de_salida
        )
        
        log.info("Ejecución desde main.py completada con éxito.")

    except Exception as e:
        log.error(f"Ha ocurrido un error durante la ejecución: {e}", exc_info=True)
    finally:
        log.info("Cerrando el navegador.")
        manager.close_browser()

if __name__ == "__main__":
    main()