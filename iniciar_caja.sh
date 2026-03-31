#!/bin/bash
echo ""
echo " ╔══════════════════════════════════════════╗"
echo " ║  La Casita Delicatessen — Sistema de Caja ║"
echo " ╚══════════════════════════════════════════╝"
echo ""

if ! command -v python3 &> /dev/null; then
    echo " ERROR: Python 3 no encontrado."
    echo " Instala desde https://www.python.org/"
    exit 1
fi

# Instalar psycopg2 si no está
python3 -c "import psycopg2" 2>/dev/null || {
    echo " Instalando dependencias..."
    pip3 install psycopg2-binary -q
}

cd "$(dirname "$0")"
echo " Iniciando sistema de caja..."
echo ""
python3 caja.py
