@echo off
title Control de polizas
cd /d "%~dp0"

echo.
echo  Iniciando Control de polizas...
echo  Se abrira el navegador en http://127.0.0.1:5000
echo  Para detener la app, presione Ctrl+C en esta ventana.
echo.

REM Espera 3 segundos y abre el navegador en una ventana oculta.
REM Asi el navegador no llega antes de que Flask este listo.
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:5000'"

REM Enciende la app con uv (segun AGENTS.md).
uv run app.py

echo.
echo La app se detuvo.
pause
