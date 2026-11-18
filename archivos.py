"""Gestión de archivos TXT, CSV y JSON con manejo de excepciones (Ítem 2)."""
import csv
import json
from pathlib import Path

from sistema import DATA_DIR, TEMP_DIR, registrar_log

CAMPOS = ["id", "fr", "fc", "spo2"]


def verificar_ruta(ruta, extension_esperada=None):
    """Verifica que la ruta sea válida y que su carpeta exista (la crea si falta)."""
    ruta = Path(ruta)
    if extension_esperada and ruta.suffix.lower() != extension_esperada:
        raise ValueError(f"Se esperaba un archivo {extension_esperada}: {ruta.name}")
    if ruta.exists() and ruta.is_dir():
        raise IsADirectoryError(f"La ruta es una carpeta, no un archivo: {ruta}")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


def guardar_txt(registros, nombre="datos_ordenados.txt"):
    """Guarda los registros en .txt (un registro por línea). Retorna la ruta o None."""
    try:
        ruta = verificar_ruta(TEMP_DIR / nombre, ".txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(" | ".join(CAMPOS) + "\n")
            for r in registros:
                f.write(" | ".join(r[c] for c in CAMPOS) + "\n")
        registrar_log(f"TXT guardado: {nombre} ({len(registros)} registros)")
        return ruta
    except (OSError, ValueError, KeyError) as e:
        registrar_log(f"Error guardando TXT: {e}", "ERROR")
        return None


def guardar_csv(registros, nombre="datos_ordenados.csv"):
    """Guarda los registros en .csv. Retorna la ruta o None."""
    try:
        ruta = verificar_ruta(TEMP_DIR / nombre, ".csv")
        with open(ruta, "w", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=CAMPOS)
            escritor.writeheader()
            escritor.writerows(registros)
        registrar_log(f"CSV guardado: {nombre} ({len(registros)} registros)")
        return ruta
    except (OSError, ValueError, csv.Error) as e:
        registrar_log(f"Error guardando CSV: {e}", "ERROR")
        return None


def exportar_json(datos, nombre="datos.json"):
    """Exporta una lista o dict a .json. Retorna la ruta o None."""
    try:
        ruta = verificar_ruta(TEMP_DIR / nombre, ".json")
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        registrar_log(f"JSON exportado: {nombre}")
        return ruta
    except (OSError, ValueError, TypeError) as e:
        registrar_log(f"Error exportando JSON: {e}", "ERROR")
        return None


def importar_json(ruta=None):
    """Importa registros desde un .json (por defecto data/json/datos.json)."""
    ruta = Path(ruta) if ruta else DATA_DIR / "json" / "datos.json"
    try:
        ruta = verificar_ruta(ruta, ".json")
        with open(ruta, "r", encoding="utf-8") as f:
            datos = json.load(f)
        if not isinstance(datos, list):
            raise ValueError("El JSON debe contener una lista de registros")
        registrar_log(f"JSON importado: {ruta.name} ({len(datos)} registros)")
        return datos
    except FileNotFoundError:
        registrar_log(f"No se encontró el archivo JSON: {ruta}", "ERROR")
    except json.JSONDecodeError as e:
        registrar_log(f"JSON mal formado en {ruta.name}: {e}", "ERROR")
    except (OSError, ValueError) as e:
        registrar_log(f"Error importando JSON: {e}", "ERROR")
    return None


def importar_csv(ruta=None):
    """Importa registros desde un .csv (por defecto data/csv/datos_ordenados.csv)."""
    ruta = Path(ruta) if ruta else DATA_DIR / "csv" / "datos_ordenados.csv"
    try:
        ruta = verificar_ruta(ruta, ".csv")
        with open(ruta, "r", newline="", encoding="utf-8") as f:
            datos = list(csv.DictReader(f))
        registrar_log(f"CSV importado: {ruta.name} ({len(datos)} registros)")
        return datos
    except FileNotFoundError:
        registrar_log(f"No se encontró el archivo CSV: {ruta}", "ERROR")
    except (OSError, ValueError, csv.Error) as e:
        registrar_log(f"Error importando CSV: {e}", "ERROR")
    return None
