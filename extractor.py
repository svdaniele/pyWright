import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def get_xpath(element):
    """Genera un XPath ottimizzato basato su ID, classi o struttura gerarchica"""
    tag = element.tag_name.lower()
    element_id = element.get_attribute("id")
    if element_id:
        return f'//*[@id="{element_id}"]'

    element_class = element.get_attribute("class")
    if element_class:
        class_list = element_class.split()
        if class_list:
            return f'//{tag}[@class="{class_list[0]}"]'

    parent = element.find_element(By.XPATH, "..")
    siblings = parent.find_elements(By.XPATH, f"./{tag}")
    if len(siblings) == 1:
        return f"{get_xpath(parent)}/{tag}"
    else:
        index = siblings.index(element) + 1
        return f"{get_xpath(parent)}/{tag}[{index}]"


# Setup del WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://findomestic.it")  # Cambia con l'URL della pagina da analizzare

    elements = driver.find_elements(By.XPATH, "/html/body//*")
    data = []

    for elem in elements:
        try:
            xpath = get_xpath(elem)
            tag = elem.tag_name.lower()

            # Estrarre solo il testo diretto (senza i figli) usando JavaScript
            text = driver.execute_script(
                "return arguments[0].childNodes[0] && arguments[0].childNodes[0].nodeType === 3 ? arguments[0].childNodes[0].nodeValue.trim() : '';",
                elem)

            # Se non ha testo visibile, prova a recuperare attributi descrittivi
            if not text:
                text = elem.get_attribute("aria-label") or elem.get_attribute("title") or elem.get_attribute(
                    "placeholder") or ""

            attributes = {
                "id": elem.get_attribute("id"),
                "class": elem.get_attribute("class"),
                "href": elem.get_attribute("href") if tag == "a" else None
            }

            if text.strip():  # Evitiamo di salvare elementi senza testo utile
                data.append({"xpath": xpath, "text": text, "tag": tag, "attributes": attributes})
        except:
            continue

    # Salva i dati in JSON
    with open("xpaths.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

finally:
    driver.quit()
