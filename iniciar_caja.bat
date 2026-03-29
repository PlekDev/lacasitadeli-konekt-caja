@echo off
title La Casita - Punto de Venta
echo.
echo   La Casita Delicatessen -- Sistema de Caja
echo   -------------------------------------------
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python no encontrado.
    echo   Descarga Python desde https://www.python.org/downloads/
    echo   Asegurate de marcar "Add Python to PATH" durante la instalacion.
    pause
    exit /b 1
)

echo   Iniciando sistema de caja...
echo.

cd /d "%~dp0"
python caja.py

if errorlevel 1 (
    echo.
    echo   Ocurrio un error al iniciar la aplicacion.
    pause
)
