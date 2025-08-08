from extract import extract_all_tables
from scripts.load import load_all_tables
from scripts.database import get_engine
from datetime import datetime

# Ruta del archivo log
LOG_FILE = "sync_log.txt"

def log_event(mensaje):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {mensaje}\n")

# Obtener motores
origin_engine = get_engine("ORIGIN_DB")
replica_engine = get_engine("DEST_DB")

# Extracción de datos
print("Extrayendo datos de la base local...")
try:
    data = extract_all_tables(origin_engine)
    print("Extracción completada.")
    log_event("Extracción exitosa de la base local.")
except Exception as e:
    mensaje = f"{type(e).__name__}: {e}"
    print(f"Error durante la extracción de datos: {mensaje}")
    log_event(f"Error durante extracción: {mensaje}")
    exit(1)

# Carga en base espejo
print("Subiendo datos a la base de réplica...")
try:
    load_all_tables(data, replica_engine)
    print("Carga completada.")
    log_event("Carga exitosa a la base de réplica.")
except Exception as e:
    mensaje = f"{type(e).__name__}: {e}"
    print(f"Error durante la carga de datos: {mensaje}")
    log_event(f"Error durante carga: {mensaje}")
    exit(1)
