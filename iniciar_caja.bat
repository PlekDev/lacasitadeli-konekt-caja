@echo off
title La Casita — Punto de Venta
color 0A
echo.
echo  ╔═══════════════════════════════════════════╗
echo  ║   La Casita Delicatessen — Sistema de Caja ║
echo  ╚═══════════════════════════════════════════╝
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python no encontrado.
    echo  Descarga desde https://www.python.org/downloads/
    echo  Marca "Add Python to PATH" al instalar.
    pause
    exit /b 1
)

REM Instalar psycopg2 si no está
python -c "import psycopg2" >nul 2>&1
if errorlevel 1 (
    echo  Instalando dependencias...
    pip install psycopg2-binary -q
)

echo  Iniciando sistema de caja...
echo.

cd /d "%~dp0"
python caja.py

if errorlevel 1 (
    echo.
    echo  Ocurrio un error. Ejecuta: python setup.py
    pause
)
