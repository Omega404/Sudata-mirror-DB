from scripts.bcra_fetch import data_intake
from logger import get_logger
from datetime import datetime
import time

log = get_logger("main_bcra.log")
start_time = time.time()

log("INICIO DEL SCRIPT DE INGESTA BCRA")
log(f"Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log("=" * 60)

try:
    data_intake()
    log("✅ Ingesta desde BCRA finalizada correctamente.")
except Exception as e:
    log(f"❌ Error durante la ingesta BCRA: {e}")

log("=" * 60)
log(f"Script finalizado en {round(time.time() - start_time, 2)} segundos")
