import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse

# Dominio objetivo
TARGET_DOMAIN = "https://argentina.slideprop.com/"
ROBOTS_URL = urljoin(TARGET_DOMAIN, "robots.txt")

def check_robot_permission(path: str, user_agent: str = "*") -> bool:
    """
    Verifica si el scraping de una ruta específica está permitido según robots.txt
    """
    rp = RobotFileParser()
    try:
        rp.set_url(ROBOTS_URL)
        rp.read()
    except Exception as e:
        print(f"[Robot] No se pudo leer robots.txt: {e}")
        return False
    
    return rp.can_fetch(user_agent, path)

def main():
    print(f"[Robot] Consultando permisos en: {ROBOTS_URL}")
    
    try:
        resp = requests.get(ROBOTS_URL, timeout=10)
        resp.raise_for_status()
        print("[Robot] robots.txt obtenido con éxito.")
    except Exception as e:
        print(f"[Robot] Error al descargar robots.txt: {e}")
        return
    
    # Solicitar tipo de inmueble
    tipo_inmueble = input("Ingrese el tipo de inmueble (ej: terrenos, casas, terrenos-casas-departamentos): ").strip().lower()
    
    # Construir la ruta
    parsed_url = urlparse(TARGET_DOMAIN)
    target_path = f"/{tipo_inmueble}-venta-posadas.html"
    
    # Validar permiso
    permitido = check_robot_permission(target_path)
    
    if permitido:
        print(f"[Robot] ✅ Permitido scrapear la ruta: {target_path}")
        print("[Robot] Puedes ejecutar tu scraper principal con seguridad.")
    else:
        print(f"[Robot] ❌ Prohibido scrapear la ruta: {target_path} según robots.txt")
        print("[Robot] Deteniendo ejecución para cumplir buenas prácticas.")
    
if __name__ == "__main__":
    main()
