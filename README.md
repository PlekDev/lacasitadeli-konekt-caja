# La Casita — Sistema de Caja (Aplicacion de Escritorio)

Aplicacion de punto de venta para uso en las cajas fisicas de La Casita Delicatessen.
Disenada para reemplazar NOVACAJA con una experiencia mas moderna y alineada al branding de La Casita.

---

## Requisitos

- **Python 3.8 o superior** (incluye tkinter por defecto en Windows y macOS)
- Sin dependencias externas — corre con Python estandar

En Linux puede ser necesario instalar tkinter:
```bash
# Ubuntu / Debian
sudo apt install python3-tk
```

---

## Iniciar la aplicacion

**Windows:**
```
iniciar_caja.bat
```

**macOS / Linux:**
```bash
chmod +x iniciar_caja.sh
./iniciar_caja.sh
```

**Directamente:**
```bash
python3 caja.py
```

---

## Atajos de teclado

| Tecla | Accion |
|-------|--------|
| F1 | Enfocar busqueda de articulos |
| F2 | Procesar cobro |
| F3 | Limpiar venta actual |
| Enter (en busqueda) | Agregar articulo si hay coincidencia unica o codigo exacto |
| Doble clic (en articulo) | Agregar al carrito |
| Escape | Limpiar busqueda |

---

## Estructura del archivo

```
caja/
  caja.py           # Aplicacion principal
  iniciar_caja.bat  # Arranque Windows
  iniciar_caja.sh   # Arranque macOS/Linux
  README.md
```

---

## Conexion con backend (pendiente)

El modulo `caja.py` incluye datos mock (`MOCK_PRODUCTS`) para desarrollo.
Al conectar con la API del backend, reemplazar las funciones:

- `_on_search_change()` — busqueda de productos via `GET /api/products?q=...`
- `_add_to_cart()` — verificacion de stock en tiempo real
- `_process_sale()` — registro de venta via `POST /api/sales`
- `init()` — login de cajero via `POST /api/auth/login`

La URL base del servidor se definira en una variable de configuracion (`API_BASE_URL`).

---

## Estado actual

- [x] Interfaz de caja completa
- [x] Busqueda de productos por nombre y codigo de barras
- [x] Carrito de compras con control de cantidades
- [x] Seleccion de metodo de pago (efectivo / tarjeta / transferencia)
- [x] Calculo automatico de cambio
- [x] Dialogo de confirmacion de venta
- [x] Atajos de teclado
- [ ] Conexion con API backend (siguiente fase)
- [ ] Login de cajero con seleccion de sucursal
- [ ] Impresion de ticket
- [ ] Apertura y cierre de caja
