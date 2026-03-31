# La Casita Delicatessen — Sistema de Caja v2

Sistema de punto de venta rediseñado, conectado a Neon PostgreSQL.

---

## Requisitos

- **Python 3.8+** (incluye tkinter)
- **psycopg2-binary** (se instala automáticamente)
- Conexión a internet para sincronizar con Neon

---

## Inicio rápido

### Windows
```
iniciar_caja.bat
```

### macOS / Linux
```bash
chmod +x iniciar_caja.sh
./iniciar_caja.sh
```

### Manual
```bash
pip install psycopg2-binary
python caja.py
```

---

## Conexión a la base de datos

La app se conecta automáticamente a:
```
Neon PostgreSQL (us-east-1)
Base: neondb
```

**Si no hay conexión:** la app funciona en modo offline con productos de prueba.

Las tablas se crean automáticamente en el primer arranque:
- `products` — catálogo de productos con stock
- `sales` — registro de ventas
- `sale_items` — detalle de cada venta

---

## Funcionalidades

| Función | Descripción |
|---------|-------------|
| 🛍 Productos en tiempo real | Se leen del stock en Neon |
| ➖ Descuento automático | Al completar una venta, el stock se descuenta en BD |
| 🔍 Búsqueda | Por nombre o SKU (con debounce 250ms) |
| 🏷 Filtros por categoría | Quesos, Carnes Frías, Vinos, etc. |
| 💳 Métodos de pago | Efectivo / Tarjeta |
| 🧾 Historial | Ventas guardadas con folio, fecha, cajero |
| 📱 Modo offline | Datos mock si no hay conexión |

---

## Atajos de teclado

| Tecla | Acción |
|-------|--------|
| F1 | Enfocar buscador |
| F2 | Procesar cobro |
| F3 | Limpiar ticket |
| Enter (en búsqueda) | Agregar si hay un solo resultado |
| Escape | Limpiar búsqueda |

---

## Estructura

```
lacasita-pos/
  caja.py            # Aplicación principal
  setup.py           # Configuración inicial
  iniciar_caja.bat   # Arranque Windows
  iniciar_caja.sh    # Arranque macOS/Linux
  README.md
```
