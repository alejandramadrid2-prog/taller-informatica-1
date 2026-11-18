"""Sistema de gestión de signos vitales - Informática 1 (Unidades 3 y 4).

Menú principal que integra: generación/ordenamiento de datos, archivos
TXT/CSV/JSON, estructura de carpetas, validación con regex y MongoDB Atlas.
"""
import datos
import archivos
import mongo_db
import sistema
import validacion


class Estado:
    """Datos en memoria durante la ejecución."""
    registros = []     # registros actuales
    coleccion = None   # colección de MongoDB (si hay conexión)
    cliente = None


# ---------------------------------------------------------------- Opciones
def ingresar_datos():
    print("\n--- Ingresar datos ---")
    print("1. Generar registros aleatorios")
    print("2. Ingresar un registro manualmente")
    op = input("Opción: ").strip()

    if op == "1":
        try:
            n = int(input("Cantidad de registros (mínimo 50) [50]: ") or 50)
        except ValueError:
            print("Cantidad inválida.")
            return
        if n < 50:
            print("El taller exige al menos 50 registros; se generarán 50.")
            n = 50
        Estado.registros = datos.ordenar_por_fc(datos.generar_registros(n))
        sistema.registrar_log(f"Generados {n} registros aleatorios y ordenados por FC")
        print(f"Se generaron {n} registros ordenados por frecuencia cardiaca.")

    elif op == "2":
        registro = {}
        for campo in ("id", "fr", "fc", "spo2"):
            while True:
                valor = input(f"{campo} ({validacion.mensaje_formato(campo)}): ").strip()
                if validacion.validar_campo(campo, valor):
                    registro[campo] = valor
                    break
                print("  Valor inválido, intenta de nuevo.")
        if any(r["id"] == registro["id"] for r in Estado.registros):
            print("Ya existe un registro con ese ID; no se agregó.")
            return
        Estado.registros.append(registro)
        Estado.registros = datos.ordenar_por_fc(Estado.registros)
        sistema.registrar_log(f"Registro ingresado manualmente: {registro['id']}")
        print("Registro agregado y datos reordenados.")
    else:
        print("Opción no válida.")


def ver_datos():
    if not Estado.registros:
        print("No hay registros cargados.")
        return
    print(f"\n{'ID':<8}{'FR':<10}{'FC':<9}{'SpO2':<6}")
    for r in Estado.registros:
        print(f"{r['id']:<8}{r['fr']:<10}{r['fc']:<9}{r['spo2']:<6}")
    print(f"Total: {len(Estado.registros)} registros (ordenados por FC)")


def validar_datos():
    if not Estado.registros:
        print("No hay registros para validar.")
        return
    validos, invalidos = validacion.validar_lista(Estado.registros)
    print(f"Válidos: {len(validos)} | Inválidos: {len(invalidos)}")
    for reg, errores in invalidos:
        print(f"  {reg.get('id', '?')}: " + "; ".join(errores))
    sistema.registrar_log(f"Validación: {len(validos)} válidos, {len(invalidos)} inválidos")
    if invalidos:
        if input("¿Eliminar los registros inválidos? (s/n): ").lower() == "s":
            Estado.registros = validos
            print("Registros inválidos eliminados.")


def exportar():
    if not Estado.registros:
        print("No hay registros para exportar.")
        return
    ordenados = datos.ordenar_por_fc(Estado.registros)
    archivos.guardar_txt(ordenados)
    archivos.guardar_csv(ordenados)
    archivos.exportar_json(ordenados)
    movidos = sistema.organizar_archivos()
    for m in movidos:
        print(f"  Guardado: {m.relative_to(sistema.BASE_DIR)}")
    print("Exportación completada.")


def importar():
    print("1. Importar JSON (data/json/datos.json)")
    print("2. Importar CSV  (data/csv/datos_ordenados.csv)")
    print("3. Importar desde otra ruta")
    op = input("Opción: ").strip()
    if op == "1":
        cargados = archivos.importar_json()
    elif op == "2":
        cargados = archivos.importar_csv()
    elif op == "3":
        ruta = input("Ruta del archivo (.json o .csv): ").strip().strip('"')
        cargados = (archivos.importar_csv(ruta) if ruta.lower().endswith(".csv")
                    else archivos.importar_json(ruta))
    else:
        print("Opción no válida.")
        return
    if cargados is None:
        print("No se pudo importar el archivo (revisa log.txt).")
        return
    validos, invalidos = validacion.validar_lista(cargados)
    Estado.registros = datos.ordenar_por_fc(validos)
    print(f"Importados {len(cargados)} registros: {len(validos)} válidos, "
          f"{len(invalidos)} descartados por no cumplir el formato.")


def conectar_mongo():
    if Estado.coleccion is not None:
        return True
    try:
        try:
            Estado.cliente, Estado.coleccion = mongo_db.conectar()
        except ValueError:
            uri = input("Pega tu cadena de conexión de MongoDB Atlas: ").strip()
            Estado.cliente, Estado.coleccion = mongo_db.conectar(uri)
        print("Conexión exitosa a MongoDB Atlas.")
        return True
    except ImportError:
        print("Falta instalar pymongo: pip install -r requirements.txt")
    except Exception as e:  # errores de red, autenticación, URI inválida...
        sistema.registrar_log(f"Error de conexión a MongoDB: {e}", "ERROR")
        print(f"No se pudo conectar a MongoDB: {e}")
    return False


def subir_a_mongo():
    if not Estado.registros:
        print("No hay registros para insertar.")
        return
    validos, invalidos = validacion.validar_lista(Estado.registros)
    if invalidos:
        print(f"Se omitirán {len(invalidos)} registros inválidos.")
    if not conectar_mongo():
        return
    try:
        n = mongo_db.insertar_registros(Estado.coleccion, validos)
        print(f"{n} registros validados insertados en 'signos_vitales'.")
    except Exception as e:
        sistema.registrar_log(f"Error insertando en MongoDB: {e}", "ERROR")
        print(f"Error insertando en MongoDB: {e}")


def consultas_mongo():
    if not conectar_mongo():
        return
    print("\n--- Consultas MongoDB ---")
    print("1. Promedio de frecuencia cardiaca")
    print("2. Documentos con SpO2 < 94")
    print("3. Buscar por ID")
    print("4. Ejecutar todo y exportar a resultados_mongo.json")
    op = input("Opción: ").strip()
    try:
        if op == "1":
            print(f"Promedio de FC: {mongo_db.promedio_fc(Estado.coleccion)} ppm")
        elif op == "2":
            docs = mongo_db.spo2_menor_a(Estado.coleccion)
            for d in docs:
                print(f"  {d['id']} | {d['fr']} | {d['fc']} | {d['spo2']}")
            print(f"Total: {len(docs)} documentos")
        elif op == "3":
            id_reg = input("ID a buscar (ej. ID-001): ").strip().upper()
            if not validacion.validar_campo("id", id_reg):
                print("ID con formato inválido.")
                return
            doc = mongo_db.buscar_por_id(Estado.coleccion, id_reg)
            print(doc if doc else "No se encontró ese ID.")
        elif op == "4":
            resultados = {
                "promedio_fc_ppm": mongo_db.promedio_fc(Estado.coleccion),
                "spo2_menor_a_94": mongo_db.spo2_menor_a(Estado.coleccion),
            }
            ruta = mongo_db.exportar_resultados(resultados)
            print(f"Resultados exportados a {ruta}" if ruta else "No se pudo exportar.")
        else:
            print("Opción no válida.")
    except Exception as e:
        sistema.registrar_log(f"Error en consulta MongoDB: {e}", "ERROR")
        print(f"Error en la consulta: {e}")


# -------------------------------------------------------------------- Menú
MENU = """
===== SISTEMA DE SIGNOS VITALES =====
1. Ingresar datos
2. Ver datos
3. Validar datos
4. Exportar archivos (TXT, CSV, JSON)
5. Importar archivos
6. Insertar registros en MongoDB
7. Consultas en MongoDB
0. Salir
"""

ACCIONES = {
    "1": ingresar_datos, "2": ver_datos, "3": validar_datos, "4": exportar,
    "5": importar, "6": subir_a_mongo, "7": consultas_mongo,
}


def main():
    if not sistema.crear_estructura():
        print("No se pudo crear la estructura de carpetas. Revisa log.txt.")
        return
    sistema.registrar_log("Programa iniciado")
    while True:
        print(MENU)
        op = input("Selecciona una opción: ").strip()
        if op == "0":
            sistema.registrar_log("Programa finalizado")
            if Estado.cliente is not None:
                Estado.cliente.close()
            print("¡Hasta luego!")
            break
        accion = ACCIONES.get(op)
        if accion:
            accion()
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
