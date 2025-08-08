from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import sys
import os
import contextlib
import re

# Configuracion del logger del navegador
@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as fnull:
        old_stderr = sys.stderr
        sys.stderr = fnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

# Configuración del navegador
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--log-level=3")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

# Inicializar WebDriver sin mostrar logs molestos
with suppress_stderr():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

# Solicitar al usuario el tipo de propiedad a buscar
entrada_usuario = input("Ingrese el tipo de inmueble (ej: terrenos, casas, terrenos-casas-departamentos): ").strip().lower()

# Validar entrada: solo letras y guiones permitidos
if not re.fullmatch(r"[a-z\-]+", entrada_usuario):
    print("Error: entrada inválida. Solo se permiten letras minúsculas y guiones (sin espacios ni caracteres especiales).")
    exit()

url = f"https://www.zonaprop.com.ar/{entrada_usuario}-venta-posadas.html"
print(f"Accediendo a la URL: {url}")
driver.get(url)

# Esperar que cargue la pagina
WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.postingsList-module__postings-container"))
)

# Extraer los links de los primeros 24 anuncios
links = []
for i in range(1, 25):
    try:
        container = driver.find_element(
            By.CSS_SELECTOR,
            f"div.postingsList-module__postings-container > div:nth-child({i})"
        )
        link = container.find_element(By.TAG_NAME, "a").get_attribute("href")
        links.append(link)
    except:
        continue

driver.quit()

# Filtrar los links que contienen "/propiedades/clasificado/"
df_links = pd.DataFrame([l for l in links if "/propiedades/clasificado/" in l], columns=["link"])
df_links.to_csv("data/aux_publicacion_inmuebles.csv", index=False)

print(f"Scraping inicial completo: {len(links)} resultados.")
print(f"{len(df_links)} links clasificados guardados en 'aux_publicacion_inmuebles.csv'.")
