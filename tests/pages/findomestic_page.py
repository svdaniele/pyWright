from .base_page import BasePage


class FindomesticPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.prestiti_personali_link = "a#menuPrestitiPersonali"
        self.prestiti_auto_link = "#menu-prestiti-personali div div:nth-child(2) div:nth-child(1) ul li:nth-child(1) a"
        self.auto_nuova_button = ":has-text('Auto Nuova')"
        self.importo_input = "input[placeholder='Importo']"
        self.conferma_button = "text='Conferma e procedi'"
        self.cookie_accept_button = "button#onetrust-accept-btn-handler"
        self.simula_rata_button = "role=link[name='Simula la rata']"

    def navigate_to_prestiti(self):
        self.page.click(self.cookie_accept_button)
        self.page.click(self.prestiti_personali_link)
        #self.page.click(self.prestiti_auto_link)
        self.page.click(self.simula_rata_button)

    def richiedi_prestito(self, importo):
        self.page.click(self.auto_nuova_button)
        self.page.fill(self.importo_input, str(importo))
        self.page.evaluate("document.activeElement.blur()")  # Per far perdere il focus
        self.page.click(self.conferma_button)
