# Sudata-BCRA

Automatización de extracción, integración y réplica de datos financieros desde la API oficial del Banco Central de la República Argentina (BCRA), junto con scraping de propiedades desde Zonaprop y una base de ventas interna.

## 📌 Objetivo

El proyecto busca mantener sincronizacion entre dos bases de datos:
- Una base local (`localhost`).
- Una base en la nube (Supabase o Neon).
- Nota: 

Además, enriquece la base con:
- **Cotizaciones históricas del dólar oficial**, obtenidas desde la API del BCRA y almacenadas con actualizaciones incrementales.
- **Datos de inmuebles en venta en Posadas (Misiones)**, extraídos automáticamente desde Zonaprop.

---

## ⚙️ Tecnologías utilizadas

- **Lenguaje:** Python
- **Librerías clave:** `requests`, `pandas`, `sqlalchemy`, `psycopg2`, `dotenv`, `selenium`
- **Automatización:** GitHub Actions, Programador de tareas (Windows)
- **Base de datos:** PostgreSQL (local y en la nube)
- **Web scraping:** Selenium + Chrome WebDriver (automático con `webdriver_manager`)

---

## 📁 scripts/
1. database.py
Función: Obtiene motores de conexión SQLAlchemy para bases de datos.

Funciones principales:

get_engine(env_var_name: str): Devuelve un engine a partir de una variable de entorno (como ORIGIN_DB o DEST_DB).

Dependencias: os, sqlalchemy, dotenv.

2. extract.py
Función: Extrae todas las tablas de la base de datos origen (exceptuando algunas).

Funciones principales:

extract_all_tables(engine): Usa sqlalchemy.inspect para obtener dinámicamente los nombres de las tablas y extraer sus datos a un diccionario de DataFrames.

Características especiales: Incluye una lista de exclusión (excluded_tables) para omitir tablas como logs o metadatos.

Dependencias: pandas, sqlalchemy.

3. load.py
Función: Carga los DataFrames extraídos en la base de datos destino.

Funciones principales:

load_all_tables(data: dict, engine): Itera sobre un diccionario {nombre_tabla: DataFrame} y los sube a la DB con to_sql.

Dependencias: pandas.

4. bcra_fetch.py
Función: Realiza ingestas incrementales de cotizaciones oficiales del dólar desde la API del BCRA.

Funciones principales:

data_intake(): Crea/verifica la tabla cotizaciones, consulta cotizaciones nuevas por día desde la última fecha registrada, e inserta nuevos registros.

create_table(), get_last_date(), api_check(), data_process(), upload_data().

Log interno: Guarda en logs/bcra_fetch.log.

Seguridad: Usa verify=False por problemas de certificados SSL con la API del BCRA.

Dependencias: requests, pandas, sqlalchemy, dotenv.

5. csv_loader.py
Función: Crea automáticamente tablas a partir de archivos CSV y las carga si no existen datos.

Funciones principales:

cargar_csvs_en_lote(directorio_csv): Lee todos los .csv del directorio y genera tablas basadas en tipos de datos, claves primarias y campos NOT NULL, definidos en config_columnas.

Configuración personalizada: Llave primaria y campos no nulos por tabla (config_columnas).

Dependencias: pandas, sqlalchemy, dotenv.

6. add_foreing_keys.py
Función: Verifica y agrega claves foráneas a la tabla factsales.

Funciones principales:

check_and_add_foreign_keys(): Si las claves no existen y los datos son consistentes, las crea.

Robustez: Incluye verificación de integridad referencial previa.

Dependencias: sqlalchemy, dotenv.

7. reset_and_reload.py
Función: Borra tablas específicas y vuelve a crear y poblarlas desde archivos CSV.

Proceso completo:

Elimina tablas (DROP TABLE).

Llama a csv_loader para recrear tablas.

Ejecuta add_foreing_keys.py para establecer relaciones.

Dependencias: sqlalchemy, dotenv, scripts externos.

8. main.py
Función: Ejecuta el flujo completo de ingesta + extracción + réplica.

Etapas:

data_intake() — Actualiza tabla cotizaciones.

extract_all_tables() — Extrae datos de todas las tablas útiles.

load_all_tables() — Replica a la base destino.

Logs: Guarda registro detallado en logs/main.log.

9. main_bcra.py
Función: Ejecuta únicamente la ingesta de cotizaciones desde BCRA.

Logs: Guarda en logs/main_bcra.log.

Uso: Ideal para programación semanal (ej. sábados).

10. main_mirror.py
Función: Solo realiza la copia espejo entre la base local y la nube.

Logs: Guarda en logs/main_mirror.log.

Uso: Programación diaria mediante GitHub Actions o Windows Task Scheduler.

11. DB_Mirror.py
Función: Script de replicación diseñado para automatización local (ej. Programador de tareas de Windows).

Flujo: Ejecuta extract_all_tables() y load_all_tables() diariamente desde localhost hacia Supabase.

Nota: Ideal para mantener sincronizada una base remota sin intervención manual.

12. logger.py
Función: Define una función log(msg) reutilizable que guarda logs en archivos .log con timestamp.

Uso compartido: Importado por main.py, main_bcra.py, main_mirror.py.



13. web_scrapper.py
Función: Permite buscar propiedades en Zonaprop según el tipo de inmueble (ej. `terrenos`, `casas`, `departamentos`, o combinaciones como `casas-terrenos`) y guarda los links de los anuncios encontrados.

- Entrada del usuario: tipo de inmueble.
- Salida:
  - `data/aux_publicacion_inmuebles.csv`: contiene los enlaces filtrados de propiedades tipo “clasificado”.
bash: python scripts/web_scrapper.py


🗂️ Archivos adicionales importantes
.env: Contiene credenciales seguras para conexión a bases (ORIGIN_DB, DEST_DB).
requirements.txt: Lista de dependencias del proyecto.
logs/: Carpeta donde se almacenan los .log de ejecución.
data/csv/: Carpeta con los archivos fuente .csv.

## ⚙️ Requisitos previos
Antes de ejecutar el proyecto, asegurate de tener instalado:

- [Python 3.11 o superior](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- Acceso a 2 bases de datos PostgreSQL (local y/o remota)
- Navegador Chrome y compatibilidad con chromedriver (gestionado automáticamente)

---

## 📥 Instalación
Luego, creá un archivo .env en la raíz con las siguientes variables:
Abrí una terminal (CMD o PowerShell) y ejecutá los siguientes pasos:

#Ingresar en terminal:
git clone https://github.com/Omega404/Sudata-mirror-DB.git
cd Sudata-mirror-DB
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

#Luego, crear un archivo .env en la raíz con las siguientes variables:
ORIGIN_DB=postgresql://usuario:contraseña@localhost:5432/tu_base_local
DEST_DB=postgresql://usuario:contraseña@host_remoto:5432/tu_base_remota

🚀 Ejecución principal
#Ejecutar scraping inicial:
python scripts/web_scrapper.py

#Extraer datos detallados:
python scripts/data_scrapper.py

#Cargar CSV como tabla:
python -c "from scripts.csv_loader import cargar_csvs_en_lote; cargar_csvs_en_lote('data')"

#Ejecutar carga incremental + réplica:
python main.py

🚀 Scripts principales
main.py - python main.py
Ejecuta el flujo completo:
Ingesta incremental desde la API del BCRA.
Extracción de todas las tablas desde la base local.
Replicación a la base en la nube.
bash: python main.py

main_mirror.py
Replica todos los datos desde la base local hacia la base en la nube (sin ejecutar la API del BCRA).
bash: python main_mirror.py

main_bcra.py
Solo realiza la ingesta incremental de cotizaciones del dólar desde la API del BCRA y actualiza la tabla cotizaciones.
bash: python main_bcra.py

🔧 Scripts auxiliares

table_uploader.py 
Permite cargar archivos CSV individuales como tablas SQL.
⚠️ Precauciones:
Solo crea la tabla si no existe.
No reemplaza ni actualiza datos existentes.
python table_uploader.py nombre_del_archivo.csv

bcra_fetch.py
Script modular que consulta la API del BCRA y actualiza la tabla cotizaciones.
⚠️ Precauciones:
No debe ejecutarse en simultáneo con main.py o main_bcra.py.
bash: python bcra_fetch.py

csv_loader.py
Carga todos los archivos CSV ubicados en /data/csv/ y crea tablas automáticamente.
⚠️ Precauciones:
Crea las tablas según la configuración de columnas y claves primarias.
No sobreescribe tablas existentes.
Ignora columnas no declaradas en la configuración.
bash: python -c "from scripts.csv_loader import cargar_csvs_en_lote; cargar_csvs_en_lote('data/csv')"

reset_and_reload.py
Elimina las tablas existentes en un orden seguro, las vuelve a crear desde los CSV y aplica las claves foráneas.
⚠️ Precauciones:
Borra completamente las tablas indicadas.
No solicita confirmación.
Solo debe usarse en entornos controlados (como desarrollo o restauración).
bash: python reset_and_reload.py

# ⚙ reespaldo en la nube
Por medio de la actualizacion de la base de datos espejo, se realiza por medio del uso de github actions, se 
realiza una copia de seguridad de una base de datos a otra, en este caso de una base en sudata, que ya era una base
espejo de una base de datos local, se le realiza una copia en neon.
