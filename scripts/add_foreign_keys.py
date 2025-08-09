from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
DB_URL = os.getenv("ORIGIN_DB")
if DB_URL is None:
    raise ValueError("Environment variable ORIGIN_DB is not set.")
engine = create_engine(DB_URL)

# Lista de claves foráneas a agregar
foreign_keys = [
    {
        "constraint_name": "fk_Customer_Segment",
        "table": "factsales",
        "column": "segmentid",
        "ref_table": "dimcustomersegment",
        "ref_column": "segmentid"
    },
    {
        "constraint_name": "fk_Dates",
        "table": "factsales",
        "column": "dateid",
        "ref_table": "dimdate",
        "ref_column": "dateid"
    },
    {
        "constraint_name": "fk_Products",
        "table": "factsales",
        "column": "productid",
        "ref_table": "dimproduct",
        "ref_column": "productid"
    }
]

def check_and_add_foreign_keys():
    with engine.begin() as conn:
        for fk in foreign_keys:
            # Verificar si ya existe el constraint con fetchone()
            result = conn.execute(text("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                AND LOWER(constraint_name) = LOWER(:name)
                AND table_name = :table
            """), {
                "name": fk["constraint_name"],
                "table": fk["table"]
            }).fetchone()

            if result:
                print(f"La foreign key '{fk['constraint_name']}' ya existe.")
                continue

            # Verificar integridad referencial antes de agregar
            invalid = conn.execute(text(f"""
                SELECT {fk['column']} FROM {fk['table']}
                WHERE {fk['column']} IS NOT NULL AND {fk['column']} NOT IN (
                    SELECT {fk['ref_column']} FROM {fk['ref_table']}
                )
                LIMIT 1
            """)).fetchone()

            if invalid:
                print(f"Integridad referencial fallida para '{fk['constraint_name']}': valor no existente en {fk['ref_table']}. No se aplicará la FK.")
                continue

            # Crear constraint
            conn.execute(text(f"""
                ALTER TABLE {fk['table']}
                ADD CONSTRAINT {fk['constraint_name']}
                FOREIGN KEY ({fk['column']})
                REFERENCES {fk['ref_table']} ({fk['ref_column']});
            """))
            print(f"Foreign key '{fk['constraint_name']}' agregada correctamente.")

if __name__ == "__main__":
    check_and_add_foreign_keys()
