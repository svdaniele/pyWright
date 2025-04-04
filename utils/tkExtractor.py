import tkinter as tk
from tkinter import ttk, messagebox
import requests
from lxml import html
import pyperclip


def generate_smart_xpath(el):
    if el.attrib.get("id"):
        return f'//*[@id="{el.attrib["id"]}"]'

    if el.attrib.get("class"):
        class_value = el.attrib["class"].split()[0]
        return f'//{el.tag}[contains(@class, "{class_value}")]'

    if el.tag in ["a", "button"] and el.text:
        text_value = el.text.strip()
        if len(text_value) < 30:
            return f'//{el.tag}[contains(text(), "{text_value}")]'

    return tree.getroottree().getpath(el)


def extract_xpaths(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        global tree
        tree = html.fromstring(response.content)
        elements = tree.xpath("//body//*")
        data = []
        for el in elements:
            try:
                if not el.tag:  # Salta elementi non validi
                    continue
                xpath = generate_smart_xpath(el)
                text = el.text_content().strip() if el.text_content() else ""
                if xpath and text:  # Salta elementi senza testo o XPath
                    data.append({"xpath": xpath, "text": text})
            except Exception as e:
                print(f"Errore nell'estrazione XPath: {e}")

        return data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Errore", f"Impossibile caricare la pagina:\n{e}")
        return []


def analyze_page():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Attenzione", "Inserisci un URL valido!")
        return
    global xpaths
    xpaths = extract_xpaths(url)
    update_results()


def update_results():
    search_term = search_entry.get().strip().lower()
    results_list.delete(*results_list.get_children())
    for item in xpaths:
        if search_term in item["text"].lower():
            results_list.insert("", "end", values=(item["text"], item["xpath"]))


def copy_xpath(event):
    selected_item = results_list.selection()
    if selected_item:
        xpath_value = results_list.item(selected_item, "values")[1]
        pyperclip.copy(xpath_value)
        messagebox.showinfo("Copiato!", "XPath copiato negli appunti!")


root = tk.Tk()
root.title("Estrattore di XPath")
root.geometry("800x500")

tk.Label(root, text="URL della pagina:", font=("Ubuntu", 12)).pack(pady=5)
text_var = tk.StringVar(root, value="https://")
url_entry = tk.Entry(root, textvariable=text_var, width=80)
url_entry.pack(pady=5)

analyze_btn = tk.Button(root, text="Analizza", command=analyze_page, font=("Ubuntu", 12))
analyze_btn.pack(pady=10)

tk.Label(root, text="Cerca testo:", font=("Ubuntu", 12)).pack(pady=5)
search_entry = tk.Entry(root, width=50)
search_entry.pack(pady=5)
search_entry.bind("<KeyRelease>", lambda event: update_results())

frame = tk.Frame(root)
frame.pack(pady=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(frame, orient="vertical")
columns = ("Testo", "XPath")
results_list = ttk.Treeview(frame, columns=columns, show="headings", height=15, yscrollcommand=scrollbar.set)
results_list.heading("Testo", text="Testo")
results_list.heading("XPath", text="XPath")

scrollbar.config(command=results_list.yview)
scrollbar.pack(side="right", fill="y")
results_list.pack(side="left", fill="both", expand=True)

results_list.bind("<Double-1>", copy_xpath)
root.mainloop()
