def load_all_tables(dataframes: dict, engine):
    for table, df in dataframes.items():
        df.to_sql(table, con=engine, if_exists='replace', index=False)
        print(f"✅ Cargada tabla {table} con {len(df)} filas")
