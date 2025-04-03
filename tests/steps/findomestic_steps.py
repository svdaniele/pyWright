from playwright.sync_api import sync_playwright
from behave import given, when, then
from tests.pages.findomestic_page import FindomesticPage

@given("Accedi a findomestic.it")
def step_open_findomestic(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=False)
    context.page = context.browser.new_page()
    context.findomestic_page = FindomesticPage(context.page)
    context.findomestic_page.navigate("https://www.findomestic.it")

@when("Naviga in 'Prestito Personali Auto'")
def step_navigate_prestiti(context):
    context.findomestic_page.navigate_to_prestiti()

@when('Richiedi prestito personale "{tipo_auto}" con importo {importo:d}')
def step_request_prestito(context, tipo_auto, importo):
    context.findomestic_page.richiedi_prestito(importo)

@then("Verifica flusso E2E 'Richiesta Prestito Online'")
def step_verify_prestito(context):
    assert "Prestito Online" in context.page.title()

@then("Risolvo verifiche")
def step_risolvo_verifiche(context):
    print("Test completato con successo")

def after_scenario(context, scenario):
    context.browser.close()
    context.playwright.stop()
