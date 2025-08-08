from scripts.database import get_engine
from scripts.extract import extract_all_tables
from scripts.load import load_all_tables
from logger import get_logger
from datetime import datetime
import time

log = get_logger("main_mirror.log")
start_time = time.time()

log("🔁 INICIO DEL SCRIPT DE COPIA A REPLICA")
log(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 60)

# Extracción desde base local
log("Extrayendo datos desde la base local...")
try:
    origin_engine = get_engine("ORIGIN_DB")
    data = extract_all_tables(origin_engine)
    log("📦 Extracción completada.")
except Exception as e:
    log(f"❌ Error durante la extracción: {e}")
    exit(1)

log("-" * 60)

# Carga hacia la base espejo
log("Cargando datos en la base destino...")
try:
    replica_engine = get_engine("DEST_DB")
    load_all_tables(data, replica_engine)
    log("✅ Carga completada.")
except Exception as e:
    log(f"❌ Error durante la carga: {e}")

log("=" * 60)
log(f"Script finalizado en {round(time.time() - start_time, 2)} segundos")
