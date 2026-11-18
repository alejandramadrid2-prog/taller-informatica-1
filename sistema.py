"""Herramientas del sistema: carpetas, movimiento de archivos y log (Ítem 3)."""
import shutil
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "salida"          # carpeta temporal donde se generan los archivos
LOG_FILE = BASE_DIR / "log.txt"

SUBCARPETAS = {
    ".txt": DATA_DIR / "txt",
    ".csv": DATA_DIR / "csv",
    ".json": DATA_DIR / "json",
}


def registrar_log(accion, nivel="INFO"):
    """Agrega una línea con fecha y hora a log.txt."""
    marca = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{marca}] [{nivel}] {accion}\n")
    except OSError as e:
        print(f"No se pudo escribir el log: {e}")


def crear_estructura():
    """Crea data/txt, data/csv, data/json y la carpeta temporal."""
    try:
        for carpeta in [*SUBCARPETAS.values(), TEMP_DIR]:
            carpeta.mkdir(parents=True, exist_ok=True)
        registrar_log("Estructura de carpetas verificada/creada (data/txt, data/csv, data/json)")
        return True
    except OSError as e:
        registrar_log(f"Error creando estructura de carpetas: {e}", "ERROR")
        return False


def mover_archivo(origen):
    """Mueve un archivo a la subcarpeta que corresponde a su extensión."""
    origen = Path(origen)
    destino_dir = SUBCARPETAS.get(origen.suffix.lower())
    if destino_dir is None:
        registrar_log(f"Extensión no soportada, no se movió: {origen.name}", "WARNING")
        return None
    try:
        if not origen.is_file():
            raise FileNotFoundError(f"No existe el archivo {origen}")
        destino_dir.mkdir(parents=True, exist_ok=True)
        destino = destino_dir / origen.name
        shutil.move(str(origen), str(destino))   # sobrescribe si ya existía
        registrar_log(f"Archivo movido: {origen.name} -> {destino.relative_to(BASE_DIR)}")
        return destino
    except (OSError, shutil.Error) as e:
        registrar_log(f"Error moviendo {origen.name}: {e}", "ERROR")
        return None


def organizar_archivos():
    """Mueve automáticamente todo lo generado en la carpeta temporal."""
    movidos = []
    if not TEMP_DIR.is_dir():
        return movidos
    for archivo in sorted(TEMP_DIR.iterdir()):
        if archivo.is_file():
            destino = mover_archivo(archivo)
            if destino:
                movidos.append(destino)
    return movidos
