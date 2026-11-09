"""Capa de datos: el único lugar del proyecto que abre archivos.

Aquí se leen el Excel de clientes y los PDF de pólizas.
No se toman decisiones del negocio (eso vive en models/polizas.py).
"""

from datetime import date, datetime
from pathlib import Path

import pandas as pd
import pdfplumber

# ---------------------------------------------------------------
# Rutas del proyecto (ladrillo: variables)
# BASE_DIR apunta a la raíz del proyecto, sin importar desde dónde
# se ejecute el programa.
# ---------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RUTA_CLIENTES = DATA_DIR / "Maestro_Clientes.xlsx"
CARPETA_POLIZAS = DATA_DIR / "polizas"

# ---------------------------------------------------------------
# Ladrillo: diccionario CAMPOS
# Relaciona la etiqueta que aparece en el PDF con el nombre del
# campo que usaremos en el diccionario de la póliza.
# ---------------------------------------------------------------
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}


# ---------------------------------------------------------------
# Funciones auxiliares (ladrillo: funciones)
# ---------------------------------------------------------------
def _limpiar_texto(valor) -> str:
    """Convierte un valor en texto y quita espacios sobrantes."""
    if valor is None:
        return ""
    # " ".join(...) convierte varios espacios seguidos en uno solo.
    return " ".join(str(valor).split()).strip()


def _normalizar_cedula(valor) -> str:
    """Devuelve la cédula como texto y sin espacios."""
    texto = "" if valor is None else str(valor)
    return texto.replace(" ", "").strip()


def _a_fecha(texto) -> date | None:
    """Convierte 'dd/mm/aaaa' en una fecha. Si está vacía o mal, None."""
    limpio = _limpiar_texto(texto)
    if not limpio:
        return None
    try:
        # Ladrillo: condicional + manejo de error.
        return datetime.strptime(limpio, "%d/%m/%Y").date()
    except ValueError:
        return None


def _a_numero(texto) -> float | None:
    """Convierte 'CRC 228,000.00' en 228000.0. Vacío o inválido, None."""
    limpio = _limpiar_texto(texto)
    if not limpio:
        return None
    # Quitamos la moneda y los separadores de miles.
    limpio = limpio.replace("CRC", "").replace(",", "").strip()
    try:
        return float(limpio)
    except ValueError:
        return None


# ---------------------------------------------------------------
# Función pública: cargar clientes
# ---------------------------------------------------------------
def cargar_clientes() -> pd.DataFrame:
    """Lee data/Maestro_Clientes.xlsx (hoja 'Clientes').

    Devuelve un DataFrame con la columna Cedula como texto sin espacios.
    """
    # dtype=str obliga a pandas a leer todo como texto (las cédulas
    # tienen guiones y no deben convertirse en números).
    # keep_default_na=False evita que las celdas vacías se vuelvan NaN.
    clientes = pd.read_excel(
        RUTA_CLIENTES,
        sheet_name="Clientes",
        dtype=str,
        keep_default_na=False,
    )

    # Ladrillo: diccionario/columna + función aplicada a cada valor.
    clientes["Cedula"] = clientes["Cedula"].map(_normalizar_cedula)
    return clientes


# ---------------------------------------------------------------
# Función pública: leer una póliza
# ---------------------------------------------------------------
def leer_poliza(ruta_pdf) -> dict:
    """Abre un PDF de póliza y devuelve sus datos en un diccionario."""
    ruta = Path(ruta_pdf)

    # Abrimos el PDF y extraemos el texto de la primera página.
    # "or ''" protege el caso en que pdfplumber no encuentre texto.
    with pdfplumber.open(ruta) as pdf:
        texto = pdf.pages[0].extract_text() or ""

    # Ladrillo: lista. Guardamos solo las líneas que tienen contenido.
    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]

    # Ladrillo: diccionario con los campos vacíos por defecto.
    # Así la póliza siempre tiene las mismas llaves, aunque falte un dato.
    poliza = {
        "archivo": ruta.name,
        "aseguradora": "",
        "numero": "",
        "ramo": "",
        "nombre": "",
        "cedula": "",
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": "",
        "suma": None,
        "asesor": "",
    }

    # Si el PDF no trajo texto, devolvemos el diccionario vacío.
    if not lineas:
        return poliza

    # La primera línea del PDF es el nombre de la aseguradora.
    poliza["aseguradora"] = lineas[0]

    # Ladrillo: bucle. Recorremos las líneas restantes buscando
    # el patrón "Etiqueta: valor".
    for linea in lineas[1:]:
        # Solo procesamos líneas que tengan dos puntos.
        if ":" not in linea:
            continue

        # split(":", 1) corta únicamente en el primer ":".
        etiqueta, valor = linea.split(":", 1)
        etiqueta = etiqueta.strip()

        # Buscamos la etiqueta en el diccionario CAMPOS.
        campo = CAMPOS.get(etiqueta)
        if campo is None:
            continue  # Etiqueta que no nos interesa (ej. Coberturas).

        valor = valor.strip()

        # Ladrillo: condicional para convertir según el tipo de dato.
        if campo in ("desde", "hasta"):
            poliza[campo] = _a_fecha(valor)
        elif campo in ("prima", "suma"):
            poliza[campo] = _a_numero(valor)
        else:
            poliza[campo] = valor

    return poliza


# ---------------------------------------------------------------
# Función pública: cargar todas las pólizas
# ---------------------------------------------------------------
def cargar_polizas() -> list[dict]:
    """Lee todos los PDF de data/polizas en orden alfabético."""
    # Ladrillo: lista ordenada de rutas (Path).
    rutas = sorted(CARPETA_POLIZAS.glob("*.pdf"), key=lambda r: r.name.lower())

    # Ladrillo: lista por comprensión; una póliza (diccionario) por PDF.
    return [leer_poliza(ruta) for ruta in rutas]
