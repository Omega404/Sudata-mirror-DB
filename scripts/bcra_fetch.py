import requests
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

# Configuracion de logger para guardardado en formato .txt
logging.basicConfig(
    filename="bcra_ingesta_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Cargar variables de entorno
load_dotenv()
DB_URL = os.getenv("ORIGIN_DB")
if DB_URL is None:
    raise ValueError("La variable ORIGIN_DB no está definida en el entorno.")
engine = create_engine(DB_URL)


# Endpoint base de la API del BCRA
API_URL = "https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones/USD"

# Nombre de la tabla
TABLE_NAME = "cotizaciones"

# Abrir o crear tabla si no existe
def create_table():
    with engine.connect() as conn:
        # Verificar si la tabla ya existe en la base de datos
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{TABLE_NAME}'
            );
        """))
        exists = result.scalar()

        if exists:  # Abrir tabla
            print(f"Tabla '{TABLE_NAME}' encontrada.")
        else:       # Crear tabla
            conn.execute(text(f"""
                CREATE TABLE {TABLE_NAME} (
                    fecha DATE PRIMARY KEY,
                    moneda TEXT NOT NULL,
                    tipo_cambio NUMERIC(10,4) NOT NULL,
                    fuente TEXT NOT NULL
                );
            """))
            print(f"🆕 Tabla '{TABLE_NAME}' creada.")


# Obtener última fecha registrada en la tabla
def get_last_date():
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT MAX(fecha) FROM {TABLE_NAME}"))
        return result.scalar()

# Llamar a la API del BCRA con rango de fechas
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def api_check(fecha_desde: str, fecha_hasta: str) -> list:
    url = f"{API_URL}?fechadesde={fecha_desde}&fechahasta={fecha_hasta}"
    response = requests.get(url, verify=False)  # 🔧 Aquí se desactiva la validación SSL
    if response.status_code != 200:
        raise Exception(f"Error al consultar la API: {response.status_code}")
    return response.json()["results"]


# Procesar datos y devolver DataFrame
def data_process(raw_data: list) -> pd.DataFrame:
    registros = []
    for dia in raw_data:
        fecha = dia["fecha"]
        for detalle in dia["detalle"]:
            registros.append({
                "fecha": fecha,
                "moneda": "Dólar",
                "tipo_cambio": detalle["tipoCotizacion"],
                "fuente": "BCRA"
            })
    df = pd.DataFrame(registros)
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date
    return df

# Insertar los datos en la tabla
def upload_data(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    df.to_sql(TABLE_NAME, con=engine, index=False, if_exists="append", method="multi")
    return len(df)

# Función principal de ingesta de datos
def data_intake():
    create_table()
    fecha_hoy = datetime.today().date()
    fecha_inicio = (datetime.today() - timedelta(days=365 * 5)).date()  # ⬅️ últimos 5 años

    # Ejecutar modo inicial o incremental
    ultima_fecha = get_last_date()
    if ultima_fecha:
        fecha_desde = ultima_fecha + timedelta(days=1)
        print(f"Modelo incremental desde {fecha_desde}")
    else:
        fecha_desde = fecha_inicio
        print(f"Modelo inicial desde {fecha_desde}")

    dias_diferencia = (fecha_hoy - fecha_desde).days

    if dias_diferencia < 0:
        print("La fecha más reciente en la tabla es posterior a la fecha actual.")
        return

    total_insertados = 0

    for i in range(dias_diferencia + 1):
        fecha_objetivo = fecha_desde + timedelta(days=i)
        try:
            datos = api_check(str(fecha_objetivo), str(fecha_objetivo))

            if not datos:
                if fecha_objetivo == fecha_hoy:
                    print(f"No se encontraron nuevas cotizaciones disponibles para {fecha_objetivo}.")
                continue

            df = data_process(datos)
            cantidad = upload_data(df)
            total_insertados += cantidad
            print(f"Cotizaciones del {fecha_objetivo} procesadas correctamente.")

        except Exception as e:
            print(f"Error al procesar {fecha_objetivo}: {e}")

    # Resumen de la ingesta
    if total_insertados > 0:
        resumen = f"Total de registros insertados: {total_insertados}"
    else:
        resumen = "No se insertaron nuevos registros."

    # Log del resumen
    print(f"\n{resumen}")
    logging.info(resumen)


# Punto de entrada principal
if __name__ == "__main__":
    print("Iniciando ingesta de cotizaciones BCRA...")
    data_intake()
