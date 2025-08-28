from core.interfaces.browser_interfaces import IBrowserFactory, IPage

class BrowserManager:
    """
    Gestiona el ciclo de vida del navegador y la página de forma agnóstica.
    """
    def __init__(self, factory: IBrowserFactory):
        self._factory = factory
        self._browser = None
        self._page = None

    def start_browser(self) -> IPage:
        self._browser = self._factory.create_browser()
        self._page = self._browser.new_page()
        return self._page

    def close_browser(self):
        if self._page and not self._page.is_closed():
            self._page.close()
        if self._browser and self._browser.is_connected():
            self._browser.close()
        # delegamos al factory (ej. para cerrar Playwright)
        if hasattr(self._factory, "stop"):
            self._factory.stop()
