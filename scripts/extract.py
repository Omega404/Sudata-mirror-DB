from sqlalchemy import inspect
import pandas as pd

def extract_all_tables(engine):
    inspector = inspect(engine)

    # Lista de tablas a excluir
    excluded_tables = ["DATES", "CUSTOMER_SEGMENTS", "PRODUCTS", "SALES", "FECHAS"]
    # Total de tablas - tablas a excluir
    tables = [t for t in inspector.get_table_names() if t not in excluded_tables]

    dataframes = {}
    for table in tables:
        try:
            df = pd.read_sql(f'SELECT * FROM "{table}"', con=engine)
            dataframes[table] = df
            print(f"Tabla '{table}' extraída con {len(df)} registros.")
        except Exception as e:
            print(f"Error al extraer la tabla '{table}': {e}")

    return dataframes