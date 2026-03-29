#!/bin/bash

echo ""
echo "  La Casita Delicatessen -- Sistema de Caja"
echo "  -------------------------------------------"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "  ERROR: Python 3 no encontrado."
    echo "  Instala Python desde https://www.python.org/downloads/"
    exit 1
fi

cd "$(dirname "$0")"
python3 caja.py
