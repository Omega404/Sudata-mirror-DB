import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
DB_URL = os.getenv("ORIGIN_DB")
if DB_URL is None:
    raise ValueError("Environment variable ORIGIN_DB is not set.")
engine = create_engine(DB_URL)

# Configuración personalizada: columnas NOT NULL y PRIMARY KEY por tabla
config_columnas = {
    "dimdate": {
        "primary_key": "dateid",
        "not_null": ["dateid", "date", "year"]
    },
    "dimcustomersegment": {
        "primary_key": "segmentid",
        "not_null": ["segmentid", "city"]
    },
    "dimproduct": {
        "primary_key": "productid",
        "not_null": ["productid", "producttype"]
    },
    "factsales": {
        "primary_key": "salesid",
        "not_null": ["salesid", "dateid", "productid", "segmentid", "price_perunit", "quantitysold"]
    },
    "inmueble_datos": {
        "primary_key": "link",
        "not_null": ["titulo", "precio", "superficie", "direccion", "latitud", "longitud", "link"]
    }
}

def cargar_csvs_en_lote(directorio_csv: str):
    for archivo in os.listdir(directorio_csv):
        if archivo.endswith(".csv"):
            ruta = os.path.join(directorio_csv, archivo)
            nombre_tabla = os.path.splitext(archivo)[0].lower()

            print(f"\nProcesando '{archivo}' como tabla '{nombre_tabla}'...")

            try:
                df = pd.read_csv(ruta)
                df.columns = [col.lower() for col in df.columns]  # Normalizar nombres a minúsculas
                columnas = df.dtypes.to_dict()

                # Config personalizada
                config = config_columnas.get(nombre_tabla, {})
                pk = config.get("primary_key")
                not_null = config.get("not_null", [])

                # Construcción de columnas SQL
                columnas_sql = []
                for col, tipo in columnas.items():
                    tipo_sql = "TEXT"
                    if "int" in str(tipo):
                        tipo_sql = "INTEGER"
                    elif "float" in str(tipo):
                        tipo_sql = "NUMERIC"

                    linea = f'"{col}" {tipo_sql}'
                    if col in not_null:
                        linea += " NOT NULL"
                    if col == pk:
                        linea += " PRIMARY KEY"
                    columnas_sql.append(linea)

                ddl = f'CREATE TABLE {nombre_tabla} (\n  {",\n  ".join(columnas_sql)}\n);'

                # Crear tabla si no existe (transacción segura)
                with engine.begin() as conn:
                    existe = conn.execute(text(f"""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = '{nombre_tabla}'
                        );
                    """)).scalar()

                    if not existe:
                        conn.execute(text(ddl))
                        print(f"Tabla '{nombre_tabla}' creada.")
                    else:
                        print(f"Tabla '{nombre_tabla}' encontrada.")

                # Insertar si la tabla está vacía
                with engine.begin() as conn:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {nombre_tabla}")).scalar()

                if count == 0:
                    df.to_sql(nombre_tabla, con=engine, index=False, if_exists='append', method='multi')
                    print(f"{len(df)} registros insertados en '{nombre_tabla}'.")
                else:
                    print(f"Tabla '{nombre_tabla}' ya contiene datos. No se insertaron duplicados.")

            except Exception as e:
                print(f"Error al procesar '{nombre_tabla}': {e}")