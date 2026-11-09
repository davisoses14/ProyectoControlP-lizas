"""Capa de negocio: reglas de las pólizas.

Aquí se decide si una póliza está vencida, por vencer o vigente.
No se abren archivos directamente: se usan las funciones de
models/datos.py. Tampoco se conoce Flask.
"""

from datetime import date

from models.datos import cargar_clientes, cargar_polizas

# ---------------------------------------------------------------
# Ladrillo: variables constantes del negocio
# FECHA_CORTE es el día con el que comparamos todas las pólizas.
# DIAS_AVISO es la ventana de anticipación para avisar al cliente.
# ---------------------------------------------------------------
FECHA_CORTE = date(2026, 11, 9)
DIAS_AVISO = 30


# ---------------------------------------------------------------
# Función: estado de una póliza
# ---------------------------------------------------------------
def estado_poliza(hasta: date | None, fecha_corte: date = FECHA_CORTE) -> str:
    """Devuelve el estado según la fecha de vencimiento (hasta).

    - Sin fecha: no se pudo leer la fecha.
    - Vencida: ya pasó la fecha de corte.
    - Por vencer: faltan entre 0 y DIAS_AVISO días.
    - Vigente: faltan más de DIAS_AVISO días.
    """
    # Ladrillo: condicional. Primero el caso sin fecha.
    if hasta is None:
        return "Sin fecha"

    # Días que faltan (puede ser negativo si ya venció).
    dias = (hasta - fecha_corte).days

    if dias < 0:
        return "Vencida"
    elif dias <= DIAS_AVISO:
        return "Por vencer"
    else:
        return "Vigente"


# ---------------------------------------------------------------
# Función: calcular todos los resultados del tablero
# ---------------------------------------------------------------
def calcular_resultados(fecha_corte: date = FECHA_CORTE) -> list[dict]:
    """Cruza pólizas con clientes y devuelve una lista ordenada.

    Cada diccionario trae los datos de la póliza más:
    correo, en_maestro, dias_para_vencer y estado.
    El orden es de menos a más días: lo urgente primero.
    """
    # Ladrillo: listas. Traemos todas las pólizas y todos los clientes.
    polizas = cargar_polizas()
    clientes = cargar_clientes()

    # Ladrillo: diccionario. Índice de clientes por cédula para
    # encontrar el correo rápido, sin recorrer toda la tabla.
    indice_clientes = {
        fila["Cedula"]: fila
        for _, fila in clientes.iterrows()
    }

    resultados = []

    # Ladrillo: bucle. Procesamos una póliza a la vez.
    for poliza in polizas:
        cliente = indice_clientes.get(poliza["cedula"])

        # Ladrillo: condicional para calcular los días.
        hasta = poliza["hasta"]
        if hasta is None:
            dias = None
        else:
            dias = (hasta - fecha_corte).days

        # Copiamos la póliza para no modificar el diccionario original.
        resultado = dict(poliza)
        resultado["correo"] = cliente["Correo"] if cliente is not None else ""
        resultado["en_maestro"] = cliente is not None
        resultado["dias_para_vencer"] = dias
        resultado["estado"] = estado_poliza(hasta, fecha_corte)

        resultados.append(resultado)

    # Ladrillo: ordenar la lista. Las pólizas sin fecha van al final
    # porque no se puede medir su urgencia.
    resultados.sort(
        key=lambda r: (
            r["dias_para_vencer"]
            if r["dias_para_vencer"] is not None
            else float("inf")
        )
    )

    return resultados


# ---------------------------------------------------------------
# Función: contar pólizas por estado
# ---------------------------------------------------------------
def contar_por_estado(resultados: list[dict]) -> dict:
    """Devuelve un diccionario con la cantidad de pólizas por estado."""
    # Ladrillo: diccionario. Arranca con los tres estados principales.
    conteos = {
        "Vigente": 0,
        "Por vencer": 0,
        "Vencida": 0,
    }

    # Ladrillo: bucle. Sumamos uno en la llave que corresponda.
    for resultado in resultados:
        estado = resultado["estado"]
        conteos[estado] = conteos.get(estado, 0) + 1

    return conteos


# ---------------------------------------------------------------
# Función: sumar primas por aseguradora
# ---------------------------------------------------------------
def primas_por_aseguradora(resultados: list[dict]) -> dict:
    """Suma las primas de las pólizas NO vencidas por aseguradora.

    Devuelve el diccionario de mayor a menor.
    """
    # Ladrillo: diccionario acumulador.
    totales = {}

    for resultado in resultados:
        # Ladrillo: condicional. Las vencidas no suman.
        if resultado["estado"] == "Vencida":
            continue

        aseguradora = resultado["aseguradora"]

        # Si la prima es None (dato faltante), sumamos 0.
        prima = resultado["prima"] or 0.0
        totales[aseguradora] = totales.get(aseguradora, 0.0) + prima

    # Ladrillo: ordenar el diccionario por su valor, de mayor a menor.
    return dict(sorted(totales.items(), key=lambda par: par[1], reverse=True))


# ---------------------------------------------------------------
# Función: buscar inconsistencias
# ---------------------------------------------------------------
def buscar_inconsistencias(resultados: list[dict]) -> list[str]:
    """Devuelve una lista de textos con los 3 tipos de problema.

    1) Cliente del maestro sin ninguna póliza.
    2) Póliza cuya cédula no está en el maestro.
    3) Póliza sin prima o con fecha ilegible.
    """
    # Ladrillo: lista de textos para ir acumulando los mensajes.
    problemas = []

    # Ladrillo: conjunto (set) con las cédulas que sí tienen póliza.
    cedulas_con_poliza = {resultado["cedula"] for resultado in resultados}

    # -----------------------------------------------------------
    # Problema 1: clientes del maestro que no aparecen en pólizas.
    # -----------------------------------------------------------
    clientes = cargar_clientes()
    for _, fila in clientes.iterrows():
        cedula = fila["Cedula"]
        if cedula not in cedulas_con_poliza:
            problemas.append(
                f"Cliente sin póliza: {fila['Nombre_Completo']} "
                f"(cédula {cedula})."
            )

    # -----------------------------------------------------------
    # Problemas 2 y 3: revisar cada póliza.
    # -----------------------------------------------------------
    for resultado in resultados:
        numero = resultado["numero"]

        if not resultado["en_maestro"]:
            problemas.append(
                f"Póliza {numero}: la cédula {resultado['cedula']} "
                f"no está en el maestro de clientes."
            )

        # Ladrillo: condicional con "or" para detectar prima faltante
        # o fecha de vencimiento ilegible.
        if resultado["prima"] is None or resultado["hasta"] is None:
            problemas.append(
                f"Póliza {numero}: falta la prima o la fecha de "
                f"vencimiento es ilegible."
            )

    return problemas


# ---------------------------------------------------------------
# Función: buscar una póliza por su número
# ---------------------------------------------------------------
def buscar_por_numero(numero: str, resultados: list[dict] | None = None) -> dict | None:
    """Devuelve la póliza con ese número, o None si no existe.

    Si no se pasan resultados, los calcula (útil para el controlador).
    """
    if resultados is None:
        resultados = calcular_resultados()

    buscado = numero.strip()

    # Ladrillo: bucle de búsqueda.
    for resultado in resultados:
        if resultado["numero"] == buscado:
            return resultado

    return None
