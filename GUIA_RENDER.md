# Guía para desplegar en Render

Esta guía explica cómo publicar **control-polizas** en Render (gratis).

---

## 1. Antes de empezar

La app ya está lista:

| Archivo | Para qué sirve en Render |
|---|---|
| `requirements.txt` | Lista de librerías que Render instala. |
| `render.yaml` | Configuración automática (Blueprint). |
| `data/` | Excel y PDF que la app lee al arrancar. **Debe estar en GitHub.** |

La app usa `gunicorn` en Render. Ese servidor **no funciona en Windows**, así que
en tu computadora sigues usando `iniciar_app.bat`.

---

## 2. Opción A: Blueprint (automático, recomendado)

1. Entra a <https://render.com> e inicia sesión con GitHub.
2. Botón **New** → **Blueprint**.
3. Elige el repositorio `davisoses14/ProyectoControlP-lizas`.
4. Render lee `render.yaml` y muestra el servicio **control-polizas**.
5. Clic en **Apply**.
6. Espera el primer despliegue (5 a 10 minutos la primera vez).

Cuando termine, la URL será algo como:

```text
https://control-polizas.onrender.com
```

---

## 3. Opción B: manual (llenando el panel)

1. **New** → **Web Service** → conecta el repositorio.
2. Llena los campos así:

| Campo | Valor |
|---|---|
| Name | `control-polizas` |
| Language / Runtime | `Python 3` |
| Branch | `main` |
| Region | `Oregon (US West)` |
| Root Directory | *(vacío)* |
| Build Command | `pip install --upgrade pip && pip install -r requirements.txt` |
| Start Command | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120` |
| Instance Type | `Free` |
| Health Check Path | `/` |

3. En **Environment Variables** agrega:

| Key | Value |
|---|---|
| `PYTHON_VERSION` | `3.12.16` |

4. Clic en **Create Web Service**.

---

## 4. Verificar que quedó bien

Abre la URL del servicio. Debes ver:

- La cabecera **azul** con “Corredora de Seguros Horizonte”.
- Los contadores **12 Vigentes / 5 Por vencer / 3 Vencidas**.
- 3 inconsistencias y las primas por aseguradora.
- El botón **Descargar todos los avisos (.zip)** funcionando.

---

## 5. Cosas importantes del plan gratis

- El servicio **se apaga solo** después de ~15 minutos sin visitas.
  La primera visita después de eso tarda 30–60 segundos en cargar.
- Los archivos que se creen en el servidor **se pierden** al reiniciar.
  Aquí no importa: la app solo lee `data/` y genera PDFs en memoria.
- Cada `push` a `main` vuelve a desplegar automáticamente.

---

## 6. Si algo falla

| Síntoma | Causa probable | Solución |
|---|---|---|
| “Application failed to respond” | El comando de inicio no usa `$PORT` | Revisa el Start Command. |
| El tablero sale vacío o con error | `data/` no está en GitHub | Haz `git add data` y push. |
| Error al instalar dependencias | Falta `requirements.txt` | Regénéralo con `uv export`. |
| Error `fcntl` en tu PC | Estás corriendo gunicorn en Windows | Usa `uv run app.py` en local. |

---

## 7. Actualizar la app

```powershell
git add .
git commit -m "Cambios en la app"
git push
```

Render detecta el push y vuelve a desplegar solo.
