from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import re
import os

# === 1. Leer links desde el archivo generado por el scraper anterior ===
archivo_origen = os.path.join("data", "aux_publicacion_inmuebles.csv")

try:
    df_links = pd.read_csv(archivo_origen)
    links_validos = df_links[df_links["link"].str.contains("/propiedades/clasificado/", na=False)]["link"].tolist()
    print(f"✅ {len(links_validos)} links cargados desde {archivo_origen}")
except Exception as e:
    print(f"❌ Error al leer {archivo_origen}: {e}")
    exit()

# === 2. Inicialización del navegador ===
def iniciar_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# === 3. Función para buscar datos dentro de la página ===
def buscar_datos(driver):
    titulo = precio = superficie = latitud = longitud = direccion = None

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except:
        pass

    try:
        titulo = driver.title.strip()
    except:
        titulo = "No detectado"

    regex_precio = re.compile(r"(USD\s*\$?\s*[\d\.,]+|\$\s*[\d\.,]+)", re.IGNORECASE)
    regex_m2 = re.compile(r"(\d{2,5})\s?m²", re.IGNORECASE)

    elementos = driver.find_elements(By.XPATH, "//div | //span")
    for el in elementos:
        try:
            texto = el.text.strip()
            if not texto:
                continue
            if not precio:
                match_precio = regex_precio.search(texto)
                if match_precio:
                    precio = match_precio.group(0)
            if not superficie:
                match_m2 = regex_m2.search(texto)
                if match_m2:
                    superficie = match_m2.group(0)
            if precio and superficie:
                break
        except:
            continue

    # Coordenadas desde <img id="static-map">
    try:
        mapa = driver.find_element(By.ID, "static-map")
        src = mapa.get_attribute("src")
        match = re.search(r"center=([-.\d]+),([-.\d]+)", src)
        if match:
            latitud, longitud = match.groups()
    except:
        latitud, longitud = None, None

    # Dirección desde div.section-location-property h4
    try:
        ubicacion_div = driver.find_element(By.CLASS_NAME, "section-location-property")
        direccion_h4 = ubicacion_div.find_element(By.TAG_NAME, "h4")
        direccion = direccion_h4.text.strip()
    except:
        direccion = None

    return titulo, precio, superficie, direccion, latitud, longitud

# === 4. Loop principal de scraping ===
resultados = []

for i, link in enumerate(links_validos, start=1):
    print(f"\n[{i}] Analizando: {link}")
    driver = iniciar_driver()
    try:
        driver.get(link)
        titulo, precio, m2, direccion, lat, lon = buscar_datos(driver)
        print(f"📌 Título: {titulo}")
        print(f"💲 Precio: {precio if precio else 'No detectado'}")
        print(f"📏 Superficie: {m2 if m2 else 'No detectado'}")
        print(f"📍 Dirección: {direccion if direccion else 'No detectado'}")
        print(f"🌐 Coordenadas: ({lat}, {lon})" if lat and lon else "🌐 Coordenadas no detectadas")
    except Exception as e:
        print(f"⚠️ Error: {e}")
        titulo = precio = m2 = direccion = lat = lon = "Error"
    finally:
        driver.quit()

    resultados.append({
        "titulo": titulo or "No detectado",
        "precio": precio or "No detectado",
        "superficie": m2 or "No detectado",
        "direccion": direccion or "No detectado",
        "latitud": lat or "No detectado",
        "longitud": lon or "No detectado",
        "link": link
    })

# === 5. Guardar resultados en CSV ===
output_path = os.path.join("data", "inmueble_datos.csv")
df = pd.DataFrame(resultados, columns=["titulo", "precio", "superficie", "direccion", "latitud", "longitud", "link"])
df.to_csv(output_path, index=False)
print(f"\n✅ Scraping finalizado. Resultados guardados en '{output_path}'")
