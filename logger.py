from datetime import datetime
import os

# Carpeta donde se guardarán los logs
LOG_FOLDER = "logs"
os.makedirs(LOG_FOLDER, exist_ok=True)

def get_logger(filename: str):
    log_path = os.path.join(LOG_FOLDER, filename)

    def log(message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
        print(message)

    return log
