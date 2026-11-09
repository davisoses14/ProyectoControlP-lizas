"""Capa de controlador: rutas de Flask.

Este archivo NO calcula nada. Solo recibe el pedido del navegador,
llama a models/ y services/, y devuelve la respuesta.
"""

import io
import zipfile

from flask import Blueprint, abort, render_template, request, send_file

from models.polizas import (
    FECHA_CORTE,
    buscar_inconsistencias,
    buscar_por_numero,
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
)
from services.generador_aviso import crear_aviso_pdf

# ---------------------------------------------------------------
# Ladrillo: Blueprint. Agrupa las rutas de pólizas para que
# app.py las registre en la aplicación Flask.
# ---------------------------------------------------------------
polizas_bp = Blueprint("polizas", __name__)


# ---------------------------------------------------------------
# Ruta 1: tablero principal
# ---------------------------------------------------------------
@polizas_bp.route("/")
def inicio():
    """Muestra el tablero con todos los resultados."""
    # Ladrillo: lista de diccionarios con las pólizas ya calculadas.
    resultados = calcular_resultados()

    # Cada dato se pide al modelo; el controlador no calcula.
    return render_template(
        "inicio.html",
        resultados=resultados,
        conteo=contar_por_estado(resultados),
        primas=primas_por_aseguradora(resultados),
        inconsistencias=buscar_inconsistencias(resultados),
        fecha_corte=FECHA_CORTE,
    )


# ---------------------------------------------------------------
# Ruta 2: ver el aviso de una póliza en PDF
# Se acepta /aviso/<numero> y también /aviso/?numero=<numero>.
# ---------------------------------------------------------------
@polizas_bp.route("/aviso/<numero>")
@polizas_bp.route("/aviso/")
def aviso(numero: str | None = None):
    """Devuelve el PDF del aviso, o 404 si no corresponde."""
    # Si no vino en la ruta, lo buscamos en la URL (?numero=...).
    numero = (numero or request.args.get("numero", "")).strip()

    resultados = calcular_resultados()
    poliza = buscar_por_numero(numero, resultados)

    # Ladrillo: condicional. No existe o está vigente => 404.
    if poliza is None or poliza["estado"] == "Vigente":
        abort(404)

    # El servicio devuelve los bytes del PDF.
    pdf = crear_aviso_pdf(poliza)

    # send_file con as_attachment=False lo muestra en el navegador.
    return send_file(
        io.BytesIO(pdf),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"aviso_{poliza['numero']}.pdf",
    )


# ---------------------------------------------------------------
# Ruta 3: descargar un .zip con todos los avisos necesarios
# ---------------------------------------------------------------
@polizas_bp.route("/descargar-avisos")
def descargar_avisos():
    """Arma en memoria un .zip con las pólizas por vencer y vencidas."""
    resultados = calcular_resultados()

    # Ladrillo: lista filtrada. Solo las que necesitan aviso.
    seleccion = [
        poliza
        for poliza in resultados
        if poliza["estado"] in ("Por vencer", "Vencida")
    ]

    # Ladrillo: BytesIO guarda el zip en memoria, sin crear archivos.
    memoria = io.BytesIO()

    # Ladrillo: bucle. Agregamos un PDF por cada póliza seleccionada.
    with zipfile.ZipFile(memoria, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
        for poliza in seleccion:
            archivo_zip.writestr(
                f"aviso_{poliza['numero']}.pdf",
                crear_aviso_pdf(poliza),
            )

    # Volvemos al inicio del archivo para poder enviarlo.
    memoria.seek(0)

    return send_file(
        memoria,
        mimetype="application/zip",
        as_attachment=True,
        download_name="avisos_renovacion.zip",
    )
