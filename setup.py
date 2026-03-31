#!/usr/bin/env python3
"""
Script de configuración — La Casita POS
Instala dependencias y prepara la base de datos Neon
"""

import subprocess
import sys
import os

DB_URL = "postgresql://neondb_owner:npg_M0gYeTvqAS6F@ep-rapid-wildflower-an0psjmg-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def instalar_psycopg2():
    print("📦 Instalando psycopg2-binary...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "psycopg2-binary"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("   ✅ psycopg2-binary instalado correctamente")
        return True
    else:
        print(f"   ❌ Error: {result.stderr}")
        return False

def probar_conexion():
    print("\n🔌 Probando conexión a Neon PostgreSQL...")
    try:
        import psycopg2
        conn = psycopg2.connect(DB_URL, connect_timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"   ✅ Conectado a: {version[:60]}...")
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ No se pudo conectar: {e}")
        print("   ⚠️  La app funcionará en modo offline con datos de prueba")
        return False

def main():
    print("=" * 55)
    print("  La Casita Delicatessen — Configuración del Sistema")
    print("=" * 55)

    ok_pip = instalar_psycopg2()
    
    if ok_pip:
        probar_conexion()

    print("\n" + "=" * 55)
    print("  ✅ Configuración completada")
    print("  → Para iniciar: python caja.py")
    print("=" * 55)

if __name__ == "__main__":
    main()
