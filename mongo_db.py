"""Gestión de MongoDB Atlas con PyMongo (Ítem 5)."""
import os

from archivos import exportar_json
from sistema import BASE_DIR, organizar_archivos, registrar_log
from validacion import extraer_numero

NOMBRE_BD = "taller_biomedico"
NOMBRE_COLECCION = "signos vitales"


def _cargar_env():
    """Lee MONGO_URI desde un archivo .env (sin dependencias extra)."""
    env = BASE_DIR / ".env"
    if env.is_file():
        for linea in env.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def conectar(uri=None):
    """Conecta con MongoDB Atlas y devuelve (cliente, coleccion). Lanza excepción si falla."""
    from pymongo import MongoClient   # import tardío: el resto del sistema funciona sin pymongo

    _cargar_env()
    uri = uri or os.environ.get("MONGO_URI")
    if not uri:
        raise ValueError("No hay cadena de conexión. Define MONGO_URI en .env o ingrésala.")
    cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
    cliente.admin.command("ping")      # verifica la conexión
    coleccion = cliente[NOMBRE_BD][NOMBRE_COLECCION]
    registrar_log(f"Conexión exitosa a MongoDB (BD: {NOMBRE_BD}, colección: {NOMBRE_COLECCION})")
    return cliente, coleccion


def _preparar_documento(registro):
    """Conserva el formato original y agrega campos numéricos para poder consultar."""
    doc = dict(registro)
    doc["fr_num"] = extraer_numero(registro["fr"])
    doc["fc_num"] = extraer_numero(registro["fc"])
    doc["spo2_num"] = extraer_numero(registro["spo2"])
    return doc


def insertar_registros(coleccion, registros):
    """Inserta los registros validados (upsert por id: no duplica al repetir)."""
    from pymongo import ReplaceOne

    if not registros:
        return 0
    operaciones = [ReplaceOne({"id": r["id"]}, _preparar_documento(r), upsert=True)
                   for r in registros]
    res = coleccion.bulk_write(operaciones)
    registrar_log(f"MongoDB: {len(registros)} registros procesados "
                  f"({res.upserted_count} nuevos, {res.modified_count} actualizados)")
    return len(registros)


def promedio_fc(coleccion):
    """Promedio de frecuencia cardiaca (en ppm)."""
    res = list(coleccion.aggregate([
        {"$group": {"_id": None, "promedio": {"$avg": "$fc_num"}, "n": {"$sum": 1}}}
    ]))
    if not res:
        return None
    promedio = round(res[0]["promedio"], 2)
    registrar_log(f"Consulta: promedio de FC = {promedio} ppm ({res[0]['n']} documentos)")
    return promedio


def spo2_menor_a(coleccion, limite=94):
    """Documentos con SpO2 menor al límite."""
    docs = list(coleccion.find({"spo2_num": {"$lt": limite}}, {"_id": 0}).sort("spo2_num", 1))
    registrar_log(f"Consulta: SpO2 < {limite} -> {len(docs)} documentos")
    return docs


def buscar_por_id(coleccion, id_registro):
    """Busca un documento por su ID (ej. 'ID-001')."""
    doc = coleccion.find_one({"id": id_registro}, {"_id": 0})
    registrar_log(f"Consulta por ID {id_registro}: {'encontrado' if doc else 'no encontrado'}")
    return doc


def exportar_resultados(resultados, nombre="resultados_mongo.json"):
    """Exporta los resultados de las consultas a resultados_mongo.json (en data/json)."""
    ruta = exportar_json(resultados, nombre)
    if ruta is None:
        return None
    movidos = organizar_archivos()
    # Devolver la ubicación final (data/json), no la ruta temporal ya movida.
    for destino in movidos:
        if destino.name == nombre:
            return destino
    return ruta
