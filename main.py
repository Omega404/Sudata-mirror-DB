from database import get_engine
from extract import extract_all_tables
from load import load_all_tables
from bcra_fetch import data_intake
from datetime import datetime
import time

LOG_FILE = "main_log.txt"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

start_time = time.time()

log("🧠 INICIO DEL SCRIPT GENERAL")
log(f"🕐 Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("="*60)

# Paso 1: Ingesta de datos BCRA
log("📥 PASO 1: Ingesta incremental desde la API del BCRA")
try:
    data_intake()
    log("✅ Ingesta desde BCRA finalizada.")
except Exception as e:
    log(f"❌ Error en la ingesta BCRA: {e}")

log("-"*60)

# Paso 2: Extracción desde base local
log("📤 PASO 2: Extracción de datos desde la base local")
try:
    origin_engine = get_engine("ORIGIN_DB")
    data = extract_all_tables(origin_engine)
    log("✅ Extracción de datos completada.")
except Exception as e:
    log(f"❌ Error durante la extracción: {e}")
    exit(1)

log("-"*60)

# Paso 3: Carga hacia la base espejo
log("📡 PASO 3: Carga de datos a la base de réplica")
try:
    replica_engine = get_engine("DEST_DB")
    load_all_tables(data, replica_engine)
    log("✅ Carga de datos completada.")
except Exception as e:
    log(f"❌ Error durante la carga: {e}")

log("="*60)
log(f"🕔 Script finalizado en {round(time.time() - start_time, 2)} segundos")

