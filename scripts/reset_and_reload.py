import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from scripts.csv_loader import cargar_csvs_en_lote
from scripts.add_foreing_keys import check_and_add_foreign_keys

# Cargar variables de entorno
load_dotenv()
DB_URL = os.getenv("ORIGIN_DB")
if DB_URL is None:
    raise ValueError("Environment variable ORIGIN_DB is not set.")
engine = create_engine(DB_URL)

# Listado de tablas a borrar (en orden inverso por FKs)
tablas_a_borrar = [
    "factsales",
    "dimproduct",
    "dimcustomersegment",
    "dimdate",
    "inmueble_datos"
]

def borrar_tablas():
    with engine.begin() as conn:
        for tabla in tablas_a_borrar:
            try:
                conn.execute(text(f'DROP TABLE IF EXISTS {tabla} CASCADE;'))
                print(f"Tabla '{tabla}' eliminada.")
            except Exception as e:
                print(f"Error al eliminar '{tabla}': {e}")

if __name__ == "__main__":
    print("Iniciando reinicialización de tablas...")
    borrar_tablas()

    print("\nCargando tablas desde CSV...")
    cargar_csvs_en_lote("data/csv")

    print("\nAplicando claves foráneas...")
    check_and_add_foreign_keys()

    print("\nProceso de reinicialización completado.")
