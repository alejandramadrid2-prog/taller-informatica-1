"""Validación de registros biomédicos con expresiones regulares (Ítem 4)."""
import re

# Patrones definidos en el apartado 1 del taller
PATRON_ID = re.compile(r"^ID-\d{3}$")             # ID-001
PATRON_FR = re.compile(r"^\d{1,3} Años$")          # 18 Años
PATRON_FC = re.compile(r"^\d{3}ppm$")              # 090ppm
PATRON_SPO2 = re.compile(r"^(?:100|\d{2})%$")      # 95%

PATRONES = {
    "id": (PATRON_ID, 'ID-001'),
    "fr": (PATRON_FR, '18 Años'),
    "fc": (PATRON_FC, '090ppm'),
    "spo2": (PATRON_SPO2, '95%'),
}


def validar_campo(campo, valor):
    """Devuelve True si el valor cumple el patrón del campo."""
    if campo not in PATRONES or not isinstance(valor, str):
        return False
    return PATRONES[campo][0].fullmatch(valor) is not None


def mensaje_formato(campo):
    """Texto de ayuda con el formato esperado de un campo."""
    return f"Formato esperado para '{campo}': {PATRONES[campo][1]}"


def validar_registro(registro):
    """Valida un registro. Retorna (es_valido, lista_de_errores)."""
    errores = []
    for campo in PATRONES:
        if campo not in registro:
            errores.append(f"Falta el campo '{campo}'")
        elif not validar_campo(campo, registro[campo]):
            errores.append(f"Campo '{campo}' inválido: {registro[campo]!r}. "
                           f"{mensaje_formato(campo)}")
    return len(errores) == 0, errores


def validar_lista(registros):
    """Separa una lista en (validos, invalidos).

    invalidos es una lista de tuplas (registro, errores).
    """
    validos, invalidos = [], []
    for reg in registros:
        ok, errores = validar_registro(reg)
        if ok:
            validos.append(reg)
        else:
            invalidos.append((reg, errores))
    return validos, invalidos


def extraer_numero(texto):
    """Extrae el entero de un campo ('090ppm' -> 90, '18 Años' -> 18)."""
    return int(re.search(r"\d+", texto).group())
