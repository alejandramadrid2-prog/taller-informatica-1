"""Generación y ordenamiento de datos biomédicos (Ítem 1)."""
import random

from validacion import extraer_numero


def generar_registros(cantidad=50):
    """Genera registros biomédicos aleatorios (mínimo 50 según el taller)."""
    registros = []
    for i in range(1, cantidad + 1):
        registros.append({
            "id": f"ID-{i:03d}",
            "fr": f"{random.randint(18, 90)} Años",
            "fc": f"{random.randint(50, 150):03d}ppm",
            "spo2": f"{random.randint(88, 100)}%",
        })
    return registros


def _clave_fc(registro):
    return extraer_numero(registro["fc"])


def _merge(izq, der, clave):
    resultado, i, j = [], 0, 0
    while i < len(izq) and j < len(der):
        if clave(izq[i]) <= clave(der[j]):   # <= mantiene la estabilidad
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1
    resultado.extend(izq[i:])
    resultado.extend(der[j:])
    return resultado


def merge_sort(lista, clave):
    """Ordenamiento por mezcla (merge sort), O(n log n), implementado a mano."""
    if len(lista) <= 1:
        return lista[:]
    medio = len(lista) // 2
    return _merge(merge_sort(lista[:medio], clave),
                  merge_sort(lista[medio:], clave), clave)


def ordenar_por_fc(registros):
    """Ordena los registros por frecuencia cardiaca (menor a mayor)."""
    return merge_sort(registros, _clave_fc)
