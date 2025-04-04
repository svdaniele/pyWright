from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
import json
import io
from io import BytesIO

# Setup WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--hide-scrollbars")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://findomestic.it"
driver.get(url)
time.sleep(3)  # Tempo di attesa per caricamento iniziale

# Ottieni dimensioni reali della pagina
total_width = driver.execute_script("return Math.max(document.body.scrollWidth, document.documentElement.scrollWidth);")
total_height = driver.execute_script(
    "return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")

print(f"Dimensioni rilevate: {total_width}x{total_height}")


# Funzione per trovare automaticamente elementi sticky/fixed
def find_sticky_elements():
    return driver.execute_script("""
        var stickyElements = [];
        var allElements = document.querySelectorAll('*');

        for (var i = 0; i < allElements.length; i++) {
            var style = window.getComputedStyle(allElements[i]);
            if (style.position === 'fixed' || style.position === 'sticky') {
                stickyElements.push(allElements[i]);
            }
        }

        return stickyElements;
    """)


# Screenshot a sezioni senza elementi sticky
def take_full_screenshot_without_sticky():
    # Imposta la dimensione della finestra per larghezza completa
    driver.set_window_size(total_width, 1000)  # Altezza fissa per ogni sezione

    # Trova elementi sticky/fixed
    sticky_elements = find_sticky_elements()
    print(f"Trovati {len(sticky_elements)} elementi sticky/fixed")

    # Salva valori originali per ripristinarli dopo
    original_styles = {}

    # Funzione per nascondere elementi sticky
    def hide_sticky_elements():
        for i, elem in enumerate(sticky_elements):
            original_style = driver.execute_script("return arguments[0].style.cssText;", elem)
            original_display = driver.execute_script("return window.getComputedStyle(arguments[0]).display;", elem)
            original_styles[i] = (original_style, original_display)
            # Nascondi l'elemento
            driver.execute_script("arguments[0].style.display = 'none';", elem)

    # Funzione per ripristinare elementi sticky
    def restore_sticky_elements():
        for i, elem in enumerate(sticky_elements):
            if i in original_styles:
                original_style, original_display = original_styles[i]
                driver.execute_script(f"arguments[0].style.cssText = '{original_style}';", elem)
                if original_display != 'none':
                    driver.execute_script(f"arguments[0].style.display = '{original_display}';", elem)

    # Calcola quante sezioni sono necessarie
    window_height = 1000
    sections = total_height // window_height + (1 if total_height % window_height > 0 else 0)

    # Crea un'immagine vuota per il risultato finale
    full_image = Image.new('RGB', (total_width, total_height))

    try:
        for i in range(sections):
            # Scorrimento alla posizione corretta
            scroll_position = i * window_height
            driver.execute_script(f"window.scrollTo(0, {scroll_position});")
            time.sleep(0.5)  # Attesa per il rendering

            # Nascondi elementi sticky prima di catturare la screenshot
            hide_sticky_elements()
            time.sleep(0.2)  # Breve attesa per l'aggiornamento del DOM

            # Cattura screenshot senza elementi sticky
            screenshot = driver.get_screenshot_as_png()
            section_image = Image.open(BytesIO(screenshot))

            # Ripristina elementi sticky per lo scrolling normale
            restore_sticky_elements()

            # Calcola la posizione y dove incollare questa sezione
            y_position = scroll_position

            # Incolla la sezione nell'immagine completa
            full_image.paste(section_image, (0, y_position))

            print(f"Catturata sezione {i + 1}/{sections} - Scroll position: {scroll_position}")
    finally:
        # Assicurati che gli elementi sticky vengano ripristinati anche in caso di errore
        restore_sticky_elements()

    return full_image


# Cattura l'immagine completa
full_image = take_full_screenshot_without_sticky()

# Salva l'immagine completa
screenshot_path = "full_screenshot.png"
full_image.save(screenshot_path)

# Extract elements and their XPaths and coordinates
elements = driver.find_elements(By.XPATH, "/html/body//*")
data = []


def get_xpath(element):
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


for elem in elements:
    try:
        xpath = get_xpath(elem)
        full_xpath = driver.execute_script(
            "function absoluteXPath(element) {"
            "var comp, comps = [];"
            "var parent = null;"
            "var xpath = '';"
            "var getPos = function(element) {"
            "var position = 1, curNode;"
            "if (element.nodeType == Node.ATTRIBUTE_NODE) return null;"
            "for (curNode = element.previousSibling; curNode; curNode = curNode.previousSibling) {"
            "if (curNode.nodeName == element.nodeName) ++position;"
            "}"
            "return position;"
            "};"
            "if (element instanceof Document) return '/';"
            "for (; element && !(element instanceof Document); element = element.nodeType == Node.ATTRIBUTE_NODE ? element.ownerElement : element.parentNode) {"
            "comp = comps[comps.length] = {};"
            "switch (element.nodeType) {"
            "case Node.TEXT_NODE:"
            "comp.name = 'text()';"
            "break;"
            "case Node.ATTRIBUTE_NODE:"
            "comp.name = '@' + element.nodeName;"
            "break;"
            "case Node.PROCESSING_INSTRUCTION_NODE:"
            "comp.name = 'processing-instruction()';"
            "break;"
            "case Node.COMMENT_NODE:"
            "comp.name = 'comment()';"
            "break;"
            "case Node.ELEMENT_NODE:"
            "comp.name = element.nodeName;"
            "break;"
            "}"
            "comp.position = getPos(element);"
            "}"
            "for (var i = comps.length - 1; i >= 0; i--) {"
            "comp = comps[i];"
            "xpath += '/' + comp.name.toLowerCase();"
            "if (comp.position !== null) xpath += '[' + comp.position + ']';"
            "}"
            "return xpath;"
            "} return absoluteXPath(arguments[0]);", elem)

        rect = driver.execute_script("""
            const rect = arguments[0].getBoundingClientRect();
            return {
                x: rect.left + window.scrollX,
                y: rect.top + window.scrollY,
                width: rect.width,
                height: rect.height
            };
        """, elem)

        text = driver.execute_script(
            "return arguments[0].childNodes[0] && arguments[0].childNodes[0].nodeType === 3 ? arguments[0].childNodes[0].nodeValue.trim() : '';",
            elem)

        if not text:
            text = elem.get_attribute("aria-label") or elem.get_attribute("title") or elem.get_attribute(
                "placeholder") or ""

        if text.strip():
            data.append({
                "xpath": xpath,
                "full_xpath": full_xpath,
                "text": text,
                "coordinates": rect
            })
    except Exception:
        continue

# Save JSON with coordinates and xpaths
json_path = "xpaths_with_coords.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Screenshot completo salvato in: {screenshot_path}")
print(f"Dati JSON salvati in: {json_path}")
print(f"Dimensioni dell'immagine salvata: {full_image.width}x{full_image.height}")

driver.quit()