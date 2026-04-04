# La Casita Delicatessen — Sistema de Caja v3

Punto de venta de escritorio conectado a Neon PostgreSQL. Parte del ecosistema **La Casita**, junto con el sistema Admin y la Página Web — los tres comparten la misma base de datos.

---

## Ecosistema La Casita

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Sistema Caja  │     │  Sistema Admin  │     │   Página Web    │
│   (este repo)   │     │                 │     │                 │
│   Python/Tk     │     │   Panel de      │     │   Catálogo y    │
│   Zebra TC52    │     │   gestión       │     │   pedidos       │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                        │
         └───────────────────────┼────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Neon PostgreSQL        │
                    │   (us-east-1)            │
                    │                          │
                    │  productos · categorias  │
                    │  ventas · detalle_venta  │
                    │  movimientos_inventario  │
                    │  usuarios                │
                    └─────────────────────────┘
```

Cualquier cambio de stock, precio o catálogo hecho en Admin se refleja en tiempo real en la caja y en la web.

---

## Requisitos

- **Python 3.8+** con `tkinter` incluido
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

La caja se conecta automáticamente al esquema compartido en Neon:

```
Host:  ep-rapid-wildflower-an0psjmg-pooler.c-6.us-east-1.aws.neon.tech
Base:  neondb
```

La cadena de conexión completa vive en `DB_URL` dentro de `caja.py`. Para cambiarla sin tocar el código, puedes exportarla como variable de entorno o usar un archivo `.env`.

**Si no hay conexión:** la app arranca en modo offline con un catálogo de productos de prueba. Las ventas realizadas en modo offline no se sincronizan con la BD.

> El esquema completo (tablas, índices, función `registrar_venta`, vistas) está en `tienda_abarrotes_schema.sql`. Solo necesita correrse una vez al crear la base de datos.

---

## Cómo funciona una venta

Cuando el cajero presiona **Cobrar**, la caja llama a la función stored `registrar_venta()` en PostgreSQL, que en una sola transacción atómica:

1. Crea el registro en `ventas` con folio `CAJA-XXXXXX`
2. Inserta cada producto en `detalle_venta` (snapshot de nombre y precio)
3. Descuenta `stock_actual` en `productos` con bloqueo de fila
4. Registra cada movimiento en `movimientos_inventario`

Si el stock de algún producto se agotó entre que se cargó en pantalla y se procesó el cobro, la transacción se revierte completa y se muestra un error al cajero sin limpiar el ticket.

---

## Funcionalidades

| Función | Descripción |
|---------|-------------|
| 🛍 Catálogo en tiempo real | Productos, precios y stock leídos desde Neon |
| 📷 Escáner Zebra TC52 | Modo HID — escanea directamente al ticket |
| ➖ Descuento atómico de stock | Vía `registrar_venta()` — sin race conditions |
| 🔍 Búsqueda con debounce | Por nombre o código de barras (250 ms) |
| 🏷 Filtros por categoría | Categorías dinámicas desde la BD |
| 💳 Métodos de pago | Efectivo (con calculadora de cambio) / Tarjeta |
| 🧾 Folios correlativos | Sincronizados con la BD al iniciar (`CAJA-000001`) |
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
  caja.py                      # Aplicación principal
  setup.py                     # Instala dependencias y prueba conexión
  tienda_abarrotes_schema.sql  # Esquema completo de la BD compartida
  iniciar_caja.bat             # Arranque Windows
  iniciar_caja.sh              # Arranque macOS / Linux
  README.md
```

---

## Usuarios de prueba

| Usuario | Contraseña |
|---------|------------|
| `prueba` | `prueba` |
| `maria` | `maria123` |
| `admin` | `admin` |

Los usuarios reales del sistema viven en la tabla `usuarios` de la BD y son gestionados desde el sistema Admin.