"""Capa de servicio: crea el PDF del aviso de renovación.

Recibe una póliza ya calculada (con nombre, estado y días) y devuelve
los bytes del PDF. No lee archivos ni conoce Flask.
"""

from fpdf import FPDF

# ---------------------------------------------------------------
# Ladrillo: variables de color y medidas
# ---------------------------------------------------------------
AZUL = (16, 69, 126)       # #10457E (azul, antes rojo #AE1800)
NEGRO = (32, 30, 29)       # #201E1D
GRIS_CLARO = (243, 242, 242)  # #F3F2F2
GRIS_TEXTO = (120, 120, 120)
BLANCO = (255, 255, 255)

ANCHO_PAGINA = 210         # A4 vertical, en milímetros
ALTO_BANDA = 32
MARGEN = 15
ANCHO_UTIL = ANCHO_PAGINA - (MARGEN * 2)
ANCHO_ETIQUETA = 55
ANCHO_VALOR = ANCHO_UTIL - ANCHO_ETIQUETA


# ---------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------
def _latin1(valor) -> str:
    """Convierte cualquier texto a latin-1 para que las tildes no fallen."""
    return str(valor).encode("latin-1", errors="replace").decode("latin-1")


def _fecha(valor) -> str:
    """Devuelve la fecha como dd/mm/aaaa, o 'Sin fecha'."""
    if not valor:
        return "Sin fecha"
    # Ladrillo: condicional. Si es una fecha, se formatea.
    return valor.strftime("%d/%m/%Y")


def _monto(valor) -> str:
    """Devuelve el monto con formato CRC, o 'No registrada'."""
    # Ladrillo: condicional para datos faltantes.
    if valor is None:
        return "No registrada"
    return f"CRC {valor:,.2f}"


def _parrafo(poliza: dict) -> str:
    """Arma el párrafo según el estado de la póliza."""
    estado = poliza.get("estado", "")
    hasta = _fecha(poliza.get("hasta"))

    # Ladrillo: condicional if / elif / else.
    if estado == "Vencida":
        return (
            f"Le informamos que su póliza venció el {hasta}. "
            f"Para conservar su protección, contáctenos y con gusto "
            f"le ayudaremos a renovarla."
        )

    elif estado == "Por vencer":
        dias = poliza.get("dias_para_vencer")
        # Ladrillo: condicional para singular y plural.
        if dias == 1:
            texto_dias = "en 1 día"
        else:
            texto_dias = f"en {dias} días"

        return (
            f"Le informamos que su póliza vence el {hasta}, {texto_dias}. "
            f"Su asesor se comunicará con usted para coordinar la renovación."
        )

    else:
        return (
            f"Su póliza se encuentra vigente y tiene cobertura hasta el "
            f"{hasta}. Le avisaremos con anticipación cuando se acerque "
            f"la fecha de renovación."
        )


# ---------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------
def crear_aviso_pdf(poliza: dict) -> bytes:
    """Crea el aviso de renovación en A4 vertical y devuelve los bytes."""
    # Ladrillo: objeto PDF con orientación vertical y medidas en mm.
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(MARGEN, MARGEN, MARGEN)
    pdf.set_auto_page_break(auto=True, margin=22)
    pdf.add_page()

    # -----------------------------------------------------------
    # Banda superior roja con los títulos
    # -----------------------------------------------------------
    pdf.set_fill_color(*AZUL)
    pdf.rect(0, 0, ANCHO_PAGINA, ALTO_BANDA, style="F")

    pdf.set_text_color(*BLANCO)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_xy(MARGEN, 8)
    pdf.cell(0, 8, _latin1("Corredora de Seguros Horizonte"))

    pdf.set_font("Helvetica", "", 12)
    pdf.set_xy(MARGEN, 18)
    pdf.cell(0, 8, _latin1("Aviso de renovación de póliza"))

    # -----------------------------------------------------------
    # Saludo y párrafo
    # -----------------------------------------------------------
    pdf.set_y(44)
    pdf.set_text_color(*NEGRO)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        8,
        _latin1(f"Estimado(a) {poliza.get('nombre', '')}:"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(2)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, _latin1(_parrafo(poliza)), align="J")
    pdf.ln(6)

    # -----------------------------------------------------------
    # Tabla de datos de la póliza
    # -----------------------------------------------------------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(
        0,
        8,
        _latin1("Datos de la póliza"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(2)

    # Ladrillo: lista de tuplas (etiqueta, valor).
    filas = [
        ("Número de póliza", poliza.get("numero", "")),
        ("Aseguradora", poliza.get("aseguradora", "")),
        ("Ramo", poliza.get("ramo", "")),
        ("Cédula", poliza.get("cedula", "")),
        (
            "Vigencia",
            f"{_fecha(poliza.get('desde'))} al {_fecha(poliza.get('hasta'))}",
        ),
        ("Prima anual", _monto(poliza.get("prima"))),
        ("Forma de pago", poliza.get("pago", "")),
    ]

    pdf.set_draw_color(190, 190, 190)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(*AZUL)
    pdf.set_text_color(*BLANCO)

    # Fila de encabezado de la tabla.
    pdf.cell(ANCHO_ETIQUETA, 8, _latin1("Dato"), border=1, fill=True)
    pdf.cell(
        ANCHO_VALOR,
        8,
        _latin1("Detalle"),
        border=1,
        fill=True,
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_text_color(*NEGRO)
    pdf.set_font("Helvetica", "", 10)

    # Ladrillo: bucle para dibujar una fila por cada dato.
    for indice, (etiqueta, valor) in enumerate(filas):
        # Ladrillo: condicional para alternar el color de fondo.
        if indice % 2 == 0:
            pdf.set_fill_color(*GRIS_CLARO)
        else:
            pdf.set_fill_color(*BLANCO)

        pdf.cell(
            ANCHO_ETIQUETA,
            8,
            _latin1(etiqueta),
            border=1,
            fill=True,
        )
        pdf.cell(
            ANCHO_VALOR,
            8,
            _latin1(valor),
            border=1,
            fill=True,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    # -----------------------------------------------------------
    # Pie de página en gris
    # Desactivamos el salto automático para que el pie no se vaya
    # a una segunda página.
    # -----------------------------------------------------------
    pdf.set_auto_page_break(auto=False)
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*GRIS_TEXTO)
    pdf.multi_cell(
        0,
        4,
        _latin1(
            "Documento ficticio para fines académicos. "
            "Universidad Fundepos - Técnico en IA Empresarial."
        ),
        align="C",
    )

    # Ladrillo: fpdf2 devuelve bytearray; lo convertimos a bytes.
    return bytes(pdf.output())
