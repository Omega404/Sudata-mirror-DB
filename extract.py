from sqlalchemy import inspect
import pandas as pd

def extract_all_tables(engine):
    inspector = inspect(engine)

    # Lista de tablas a excluir del proceso (vacía en este caso)
    tablas_excluidas = set()

    # Obtener todas las tablas, excluyendo las de la lista
    tables = [t for t in inspector.get_table_names() if t not in tablas_excluidas]

    dataframes = {}
    for table in tables:
        try:
            df = pd.read_sql(f'SELECT * FROM "{table}"', con=engine)
            dataframes[table] = df
            print(f"📊 Tabla '{table}' extraída con {len(df)} registros.")
        except Exception as e:
            print(f"❌ Error al extraer la tabla '{table}': {e}")

    return dataframes