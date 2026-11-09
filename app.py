"""Arranque de la aplicación Flask.

Crea la app con las carpetas de vistas y archivos estáticos,
y registra el Blueprint de pólizas.
"""

from flask import Flask

from controllers.polizas_controller import polizas_bp

# ---------------------------------------------------------------
# Ladrillo: variable app. Es la aplicación Flask.
# template_folder="views"      -> plantillas HTML (Jinja)
# static_folder="public/static" -> CSS
# static_url_path="/static"     -> las rutas del CSS empiezan con /static
# ---------------------------------------------------------------
app = Flask(
    __name__,
    template_folder="views",
    static_folder="public/static",
    static_url_path="/static",
)

# Registramos las rutas del controlador.
app.register_blueprint(polizas_bp)


# ---------------------------------------------------------------
# Ladrillo: condicional. El servidor solo arranca si este archivo
# se ejecuta directamente (no cuando se importa para una prueba).
# ---------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
