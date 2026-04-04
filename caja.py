"""
La Casita Delicatessen — Sistema de Caja v3
Rediseño moderno · Neon PostgreSQL · Zebra TC52 · Pointer-ready
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import os

# ── Intentar importar psycopg2 ──────────────────────────────────
try:
    import psycopg2
    import psycopg2.extras
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# ── Configuración de Base de Datos ──────────────────────────────
DB_URL = "postgresql://neondb_owner:npg_M0gYeTvqAS6F@ep-rapid-wildflower-an0psjmg-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# ── PALETA LA CASITA ────────────────────────────────────────────
C = {
    "bg":           "#F5F2ED",
    "bg2":          "#EDEAE3",
    "surface":      "#FFFFFF",
    "surface2":     "#FAFAF8",
    "border":       "#E2DDD5",
    "border2":      "#CCC7BC",
    "text":         "#1A1814",
    "text2":        "#5C574E",
    "text3":        "#9C978E",
    "green":        "#1E4D35",
    "green_hover":  "#2A6647",
    "green_mid":    "#3A8560",
    "green_light":  "#6DB88A",
    "green_pale":   "#E8F4ED",
    "green_tag":    "#D1EAD9",
    "amber":        "#A0520A",
    "amber_bg":     "#FEF3C7",
    "amber_pale":   "#FFF8E7",
    "red":          "#B91C1C",
    "red_bg":       "#FEE2E2",
    "red_pale":     "#FFF5F5",
    "header":       "#162C20",
    "header2":      "#1E3D2A",
    "header_text":  "#E8F2EC",
    "header_dim":   "#8AB89A",
    "card_hover":   "#F0EDE7",
    "chip_green":   "#D4EDDA",
    "chip_red":     "#FFD6D6",
    "chip_amber":   "#FFE9B3",
}

F = "Segoe UI"

def ff(size=10, weight="normal"):
    return (F, size, weight)

def fm(size=10, weight="normal"):
    return ("Consolas", size, weight)


# ── DATOS MOCK (fallback si no hay BD) ──────────────────────────
MOCK_PRODUCTS = [
    {"id": 1,  "codigo_barras": "QSO-001", "nombre": "Queso Manchego",       "precio_venta": 189.00, "stock_actual": 24, "categoria": "Quesos",       "emoji": "🧀"},
    {"id": 2,  "codigo_barras": "CRN-002", "nombre": "Jamón Serrano",         "precio_venta": 320.00, "stock_actual": 5,  "categoria": "Carnes Frías", "emoji": "🥩"},
    {"id": 3,  "codigo_barras": "VIN-003", "nombre": "Vino Tinto Reserva",    "precio_venta": 285.00, "stock_actual": 12, "categoria": "Vinos",        "emoji": "🍷"},
    {"id": 4,  "codigo_barras": "PAN-004", "nombre": "Pan Baguette",          "precio_venta":  45.00, "stock_actual": 20, "categoria": "Panadería",    "emoji": "🥖"},
    {"id": 5,  "codigo_barras": "ACE-005", "nombre": "Aceite de Oliva Extra", "precio_venta": 198.00, "stock_actual":  9, "categoria": "Aceites",      "emoji": "🫒"},
    {"id": 6,  "codigo_barras": "DLC-006", "nombre": "Chocolate Belga",       "precio_venta": 125.00, "stock_actual":  3, "categoria": "Dulces",       "emoji": "🍫"},
    {"id": 7,  "codigo_barras": "QSO-007", "nombre": "Queso Brie",            "precio_venta": 165.00, "stock_actual":  7, "categoria": "Quesos",       "emoji": "🧀"},
    {"id": 8,  "codigo_barras": "CRN-008", "nombre": "Salami Italiano",       "precio_venta": 145.00, "stock_actual":  0, "categoria": "Carnes Frías", "emoji": "🥩"},
    {"id": 9,  "codigo_barras": "VIN-009", "nombre": "Prosecco Brut",         "precio_venta": 310.00, "stock_actual": 15, "categoria": "Vinos",        "emoji": "🥂"},
    {"id": 10, "codigo_barras": "PAN-010", "nombre": "Croissant Mantequilla", "precio_venta":  38.00, "stock_actual": 18, "categoria": "Panadería",    "emoji": "🥐"},
    {"id": 11, "codigo_barras": "DLC-011", "nombre": "Mermelada Artesanal",   "precio_venta":  89.00, "stock_actual":  2, "categoria": "Dulces",       "emoji": "🍓"},
    {"id": 12, "codigo_barras": "QSO-011", "nombre": "Queso Gouda",           "precio_venta": 175.00, "stock_actual": 11, "categoria": "Quesos",       "emoji": "🧀"},
    {"id": 13, "codigo_barras": "CRN-012", "nombre": "Paté de Campaña",       "precio_venta": 110.00, "stock_actual":  6, "categoria": "Carnes Frías", "emoji": "🍖"},
    {"id": 14, "codigo_barras": "ACE-014", "nombre": "Vinagre Balsámico",     "precio_venta": 155.00, "stock_actual":  8, "categoria": "Aceites",      "emoji": "🫙"},
    {"id": 15, "codigo_barras": "PAN-015", "nombre": "Pan de Nuez",           "precio_venta":  62.00, "stock_actual": 14, "categoria": "Panadería",    "emoji": "🍞"},
    {"id": 16, "codigo_barras": "DLC-016", "nombre": "Turrón de Almendra",    "precio_venta":  95.00, "stock_actual":  6, "categoria": "Dulces",       "emoji": "🍬"},
]

MOCK_USER     = {"id": 2, "name": "Cajero 1", "role": "cajero"}
MOCK_LOCATION = {"id": "L01", "name": "Sucursal Centro"}

# Folio counter — se sincroniza con BD al conectar
FOLIO_COUNTER = [0]

# ── Usuarios del sistema (login local para la caja) ─────────────
SYSTEM_USERS = {
    "prueba": ("prueba",   "Usuario Prueba",   None),
    "maria":  ("maria123", "María G.",          None),
    "admin":  ("admin",    "Administrador",     None),
}


# ════════════════════════════════════════════════════════════════
#  DATABASE MANAGER — conectado al esquema tienda_abarrotes
#  Tablas: productos, categorias, ventas, detalle_venta,
#          movimientos_inventario, usuarios
#  Función stored: registrar_venta()
# ════════════════════════════════════════════════════════════════
class DBManager:
    def __init__(self):
        self.conn      = None
        self.connected = False
        self._connect()

    # ── Conexión ────────────────────────────────────────────────
    def _connect(self):
        if not DB_AVAILABLE:
            print("[DB] psycopg2 no disponible — modo offline")
            return
        try:
            self.conn = psycopg2.connect(DB_URL, connect_timeout=8)
            self.conn.autocommit = False
            self.connected = True
            print("[DB] Conectado a Neon PostgreSQL")
            self._sync_folio_counter()
        except Exception as e:
            print(f"[DB] No se pudo conectar: {e}")
            self.connected = False

    # ── Sincroniza el contador de folios con la BD ──────────────
    def _sync_folio_counter(self):
        """Lee el último folio CAJA-XXXXXX y ajusta el contador local."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT folio FROM ventas
                WHERE canal = 'caja' AND folio LIKE 'CAJA-%'
                ORDER BY id DESC LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                try:
                    num = int(row[0].split("-")[1])
                    FOLIO_COUNTER[0] = num
                    print(f"[DB] Último folio encontrado: {row[0]}")
                except:
                    FOLIO_COUNTER[0] = 0
            else:
                FOLIO_COUNTER[0] = 0
        except Exception as e:
            print(f"[DB] _sync_folio_counter error: {e}")

    # ── Reconexión automática ───────────────────────────────────
    def _ensure_connection(self):
        """Intenta reconectar si la conexión se cayó."""
        if not self.connected:
            return False
        try:
            self.conn.cursor().execute("SELECT 1")
            return True
        except:
            print("[DB] Conexión perdida — intentando reconectar...")
            try:
                self.conn = psycopg2.connect(DB_URL, connect_timeout=5)
                self.conn.autocommit = False
                print("[DB] Reconectado")
                return True
            except Exception as e:
                print(f"[DB] Reconexión fallida: {e}")
                self.connected = False
                return False

    # ──────────────────────────────────────────────────────────────
    #  PRODUCTOS
    #  Lee de: productos JOIN categorias
    #  Campos usados por la UI: id, codigo_barras, nombre,
    #    precio_venta, stock_actual, categoria (nombre), emoji
    # ──────────────────────────────────────────────────────────────
    def get_products(self, search="", category="Todos"):
        if not self._ensure_connection():
            return self._filter_mock(search, category)
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            q = """
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nombre,
                    p.precio_venta,
                    p.stock_actual,
                    p.stock_minimo,
                    c.nombre AS categoria,
                    COALESCE(p.imagen_url, '📦') AS emoji
                FROM productos p
                LEFT JOIN categorias c ON c.id = p.categoria_id
                WHERE p.activo = TRUE
            """
            params = []
            if search:
                q += " AND (LOWER(p.nombre) LIKE %s OR LOWER(p.codigo_barras) LIKE %s)"
                params += [f"%{search.lower()}%", f"%{search.lower()}%"]
            if category and category != "Todos":
                q += " AND c.nombre = %s"
                params.append(category)
            q += " ORDER BY c.nombre, p.nombre"
            cur.execute(q, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"[DB] get_products error: {e}")
            try: self.conn.rollback()
            except: pass
            return self._filter_mock(search, category)

    def get_product_by_barcode(self, barcode):
        """Búsqueda exacta por código de barras — para escáner Zebra TC52."""
        if not self._ensure_connection():
            match = next((p for p in MOCK_PRODUCTS
                          if p["codigo_barras"].lower() == barcode.lower()), None)
            return match
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT
                    p.id,
                    p.codigo_barras,
                    p.nombre,
                    p.precio_venta,
                    p.stock_actual,
                    p.stock_minimo,
                    c.nombre AS categoria,
                    COALESCE(p.imagen_url, '📦') AS emoji
                FROM productos p
                LEFT JOIN categorias c ON c.id = p.categoria_id
                WHERE p.activo = TRUE
                  AND LOWER(p.codigo_barras) = LOWER(%s)
            """, (barcode,))
            row = cur.fetchone()
            return dict(row) if row else None
        except Exception as e:
            print(f"[DB] get_product_by_barcode error: {e}")
            return None

    def get_stock(self, product_id):
        """Stock en tiempo real directamente desde la BD."""
        if not self._ensure_connection():
            p = next((x for x in MOCK_PRODUCTS if x["id"] == product_id), None)
            return p["stock_actual"] if p else 0
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT stock_actual FROM productos WHERE id = %s", (product_id,))
            row = cur.fetchone()
            return row[0] if row else 0
        except Exception as e:
            print(f"[DB] get_stock error: {e}")
            return 0

    def _filter_mock(self, search, category):
        result = MOCK_PRODUCTS
        if search:
            result = [p for p in result
                      if search.lower() in p["nombre"].lower()
                      or search.lower() in p["codigo_barras"].lower()]
        if category and category != "Todos":
            result = [p for p in result if p.get("categoria") == category]
        return result

    # ──────────────────────────────────────────────────────────────
    #  CATEGORÍAS
    #  Devuelve lista de nombres activos para los chips de filtro
    # ──────────────────────────────────────────────────────────────
    def get_categories(self):
        if not self._ensure_connection():
            return ["Quesos", "Carnes Frías", "Vinos", "Panadería", "Dulces", "Aceites"]
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT DISTINCT c.nombre
                FROM categorias c
                JOIN productos p ON p.categoria_id = c.id
                WHERE c.activo = TRUE AND p.activo = TRUE
                ORDER BY c.nombre
            """)
            return [row[0] for row in cur.fetchall()]
        except Exception as e:
            print(f"[DB] get_categories error: {e}")
            return []

    # ──────────────────────────────────────────────────────────────
    #  REGISTRAR VENTA
    #  Usa la función stored registrar_venta() del esquema, que:
    #    1. Crea el registro en ventas
    #    2. Inserta detalle_venta por cada producto
    #    3. Descuenta stock en productos
    #    4. Registra movimientos_inventario
    #  Todo en una transacción atómica con bloqueo de filas.
    # ──────────────────────────────────────────────────────────────
    def save_sale(self, folio, cart, total, subtotal, tax, payment,
                  cashier, location, usuario_id=None):
        """
        Parámetros:
          folio       — str  ej. "CAJA-000042"
          cart        — list de dicts con claves: product, qty, subtotal
          total       — float total incluyendo IVA
          subtotal    — float sin IVA
          tax         — float IVA
          payment     — str "efectivo" | "tarjeta" | "transferencia"
          cashier     — str nombre del cajero
          location    — str nombre de la sucursal
          usuario_id  — int ID del usuario en tabla usuarios (puede ser None)

        Retorna: (venta_id: int | None, error: str | None)
        """
        if not self._ensure_connection():
            print("[DB] Sin conexión — venta guardada solo localmente")
            return None, "sin_conexion"

        # Construir el JSON de items para la función stored
        import json
        items_json = json.dumps([
            {
                "producto_id":    item["product"]["id"],
                "cantidad":       item["qty"],
                "precio_unitario": float(item["product"]["precio_venta"])
            }
            for item in cart
        ])

        # Resolver usuario_id: si no viene, buscar el cajero en la tabla usuarios
        uid = usuario_id
        if uid is None:
            uid = self._get_or_create_user_id(cashier)

        try:
            cur = self.conn.cursor()

            # ── Llamar a la función stored del esquema ──────────
            cur.execute("""
                SELECT registrar_venta(%s, %s, %s, %s, %s::jsonb)
            """, (folio, "caja", uid, payment, items_json))

            venta_id = cur.fetchone()[0]
            self.conn.commit()
            print(f"[DB] Venta registrada — folio: {folio}, id: {venta_id}")
            return venta_id, None

        except psycopg2.errors.RaiseException as e:
            # Errores de negocio lanzados por la función (stock insuficiente, etc.)
            try: self.conn.rollback()
            except: pass
            msg = str(e).split("\n")[0]
            print(f"[DB] Error de negocio en registrar_venta: {msg}")
            return None, msg

        except Exception as e:
            try: self.conn.rollback()
            except: pass
            print(f"[DB] save_sale error inesperado: {e}")
            return None, str(e)

    def _get_or_create_user_id(self, display_name):
        """
        Intenta encontrar en la tabla usuarios el id que corresponde
        al cajero activo. Si no lo encuentra, usa el usuario cajero por defecto.
        Nunca falla — devuelve None si no puede resolver.
        """
        try:
            cur = self.conn.cursor()
            # Buscar por nombre de display
            cur.execute("""
                SELECT id FROM usuarios
                WHERE nombre = %s AND activo = TRUE
                LIMIT 1
            """, (display_name,))
            row = cur.fetchone()
            if row:
                return row[0]
            # Fallback: primer cajero activo
            cur.execute("""
                SELECT id FROM usuarios
                WHERE rol = 'cajero' AND activo = TRUE
                ORDER BY id LIMIT 1
            """)
            row = cur.fetchone()
            return row[0] if row else None
        except:
            return None

    # ──────────────────────────────────────────────────────────────
    #  UPDATE STOCK MANUAL (ajuste directo, fuera de una venta)
    #  Solo para correcciones manuales; las ventas ya descuentan stock
    #  a través de registrar_venta().
    # ──────────────────────────────────────────────────────────────
    def update_stock(self, product_id, delta, usuario_id=None, motivo="Ajuste manual"):
        """
        Ajusta el stock y registra el movimiento en movimientos_inventario.
        delta negativo = salida, positivo = entrada.
        """
        if not self._ensure_connection():
            for p in MOCK_PRODUCTS:
                if p["id"] == product_id:
                    p["stock_actual"] = max(0, p["stock_actual"] + delta)
            return True
        try:
            cur = self.conn.cursor()

            # Leer stock actual con bloqueo
            cur.execute("""
                SELECT stock_actual FROM productos
                WHERE id = %s FOR UPDATE
            """, (product_id,))
            row = cur.fetchone()
            if not row:
                self.conn.rollback()
                return False

            stock_antes  = row[0]
            stock_despues = max(0, stock_antes + delta)

            # Actualizar stock
            cur.execute("""
                UPDATE productos
                SET stock_actual = %s
                WHERE id = %s
            """, (stock_despues, product_id))

            # Registrar movimiento
            cur.execute("""
                INSERT INTO movimientos_inventario
                    (producto_id, usuario_id, tipo, cantidad,
                     stock_antes, stock_despues, motivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (product_id, usuario_id, "ajuste", delta,
                  stock_antes, stock_despues, motivo))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB] update_stock error: {e}")
            try: self.conn.rollback()
            except: pass
            return False

    # ──────────────────────────────────────────────────────────────
    #  VENTAS DEL DÍA (para historial / reporte rápido)
    # ──────────────────────────────────────────────────────────────
    def get_today_sales(self):
        if not self._ensure_connection():
            return []
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT
                    v.id,
                    v.folio,
                    v.canal,
                    v.total,
                    v.subtotal,
                    v.metodo_pago  AS payment,
                    u.nombre       AS cashier,
                    v.created_at
                FROM ventas v
                LEFT JOIN usuarios u ON u.id = v.usuario_id
                WHERE v.estado = 'completada'
                  AND v.created_at::date = CURRENT_DATE
                ORDER BY v.created_at DESC
                LIMIT 50
            """)
            return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            print(f"[DB] get_today_sales error: {e}")
            return []

    def close(self):
        if self.conn:
            try: self.conn.close()
            except: pass


# ════════════════════════════════════════════════════════════════
#  ZEBRA TC52 — BARCODE SCANNER HANDLER (HID / Keyboard Wedge)
# ════════════════════════════════════════════════════════════════
class BarcodeScanner:
    TIMEOUT_MS = 120
    MIN_LENGTH  = 4

    def __init__(self, root, callback):
        self.root     = root
        self.callback = callback
        self._buffer  = []
        self._last_t  = 0
        root.bind_all("<KeyPress>", self._on_key, add="+")

    def _on_key(self, event):
        now = time.time() * 1000

        if now - self._last_t > self.TIMEOUT_MS and self._buffer:
            self._buffer = []

        self._last_t = now
        char = event.char

        if event.keysym == "Return":
            scanned = "".join(self._buffer).strip()
            self._buffer = []
            if len(scanned) >= self.MIN_LENGTH:
                self.callback(scanned)
        elif char and char.isprintable():
            self._buffer.append(char)
        else:
            if event.keysym not in ("Shift_L", "Shift_R", "Caps_Lock"):
                pass


# ════════════════════════════════════════════════════════════════
#  TOAST
# ════════════════════════════════════════════════════════════════
class Toast(tk.Toplevel):
    def __init__(self, master, message, type_="success", duration=1800):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)

        bg = {"success": C["green"], "error": C["red"], "warning": C["amber"]}.get(type_, C["green"])

        frame = tk.Frame(self, bg=bg, padx=20, pady=12)
        frame.pack()

        icon = {"success": "✓", "error": "✕", "warning": "⚠"}.get(type_, "✓")
        tk.Label(frame, text=f"  {icon}  {message}", font=ff(10, "bold"),
                 bg=bg, fg="white").pack()

        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + master.winfo_height() - 80
        self.geometry(f"+{x}+{y}")
        self._fade_in(duration)

    def _fade_in(self, duration, step=0):
        alpha = min(1.0, step * 0.1)
        try:
            self.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.after(30, lambda: self._fade_in(duration, step + 1))
            else:
                self.after(duration, self._fade_out)
        except: pass

    def _fade_out(self, step=10):
        alpha = max(0.0, step * 0.1)
        try:
            self.attributes("-alpha", alpha)
            if alpha > 0:
                self.after(40, lambda: self._fade_out(step - 1))
            else:
                self.destroy()
        except: pass


# ════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ════════════════════════════════════════════════════════════════
class CajaApp(tk.Tk):
    def __init__(self, logged_user=None):
        super().__init__()

        self.title("La Casita — Punto de Venta")
        self.geometry("1400x860")
        self.minsize(1200, 720)
        self.configure(bg=C["bg"])

        self.user     = logged_user if logged_user else MOCK_USER
        self.location = MOCK_LOCATION
        self.cart     = []
        self.pay_var  = tk.StringVar(value="efectivo")
        self.products = []
        self.active_category = tk.StringVar(value="Todos")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self._search_after = None

        # DB
        self.db = DBManager()
        self._db_status = "🟢 Neon conectado" if self.db.connected else "🟡 Modo offline"

        # Cargar categorías dinámicamente desde la BD
        self._categories = ["Todos"] + self.db.get_categories()
        if len(self._categories) <= 1:
            # fallback si la BD no tiene datos aún
            self._categories = [
                "Todos", "Abarrotes", "Bebidas", "Lácteos",
                "Limpieza", "Botanas", "Panadería", "Carnes frías", "Higiene"
            ]

        self._build_ui()
        self._load_products()
        self._start_clock()

        # Escáner Zebra TC52
        self.scanner = BarcodeScanner(self, self._on_barcode_scanned)

    # ──────────────────────────────────────────────────────────────
    #  ZEBRA TC52 — callback cuando se escanea un código de barras
    # ──────────────────────────────────────────────────────────────
    def _on_barcode_scanned(self, code):
        product = self.db.get_product_by_barcode(code)
        if product:
            self._add_to_cart(product)
            self.entry_search.config(bg="#E8F4ED")
            self.after(300, lambda: self.entry_search.config(bg=C["surface"]))
        else:
            Toast(self, f"Código no encontrado: {code}", "error", 2500)

    # ────────────────────────────────────────────────────────────
    #  BUILD UI
    # ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_body()

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["header"], height=56)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        left = tk.Frame(hdr, bg=C["header"])
        left.pack(side="left", padx=20, pady=10)

        logo_frame = tk.Frame(left, bg="#2A5240", padx=8, pady=4)
        logo_frame.pack(side="left")
        tk.Label(logo_frame, text="LC", font=ff(12, "bold"),
                 bg="#2A5240", fg="white").pack()

        tk.Frame(left, bg="#3D6B50", width=1).pack(side="left", fill="y", pady=6, padx=14)

        brand_info = tk.Frame(left, bg=C["header"])
        brand_info.pack(side="left")
        tk.Label(brand_info, text="La Casita", font=ff(13, "bold"),
                 bg=C["header"], fg=C["header_text"]).pack(anchor="w")
        tk.Label(brand_info, text="caja", font=ff(7, "bold"),
                 bg=C["header"], fg=C["header_dim"]).pack(anchor="w")

        center = tk.Frame(hdr, bg=C["header"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        caja_badge = tk.Frame(center, bg=C["header2"], padx=12, pady=4)
        caja_badge.pack(side="left", padx=8)
        self.lbl_session_dot = tk.Label(caja_badge, text="●", font=ff(8),
                                         bg=C["header2"], fg=C["green_light"])
        self.lbl_session_dot.pack(side="left", padx=(0, 4))
        tk.Label(caja_badge, text="Caja abierta · Turno 1", font=ff(9),
                 bg=C["header2"], fg=C["header_text"]).pack(side="left")

        tk.Label(center, text="Ventas", font=ff(9),
                 bg=C["header"], fg=C["header_dim"],
                 cursor="hand2", padx=10).pack(side="left")

        suc_frame = tk.Frame(center, bg=C["header2"], padx=10, pady=4)
        suc_frame.pack(side="left", padx=8)
        tk.Label(suc_frame, text=f"🏪  {self.location['name']} ∨", font=ff(9),
                 bg=C["header2"], fg=C["header_text"]).pack()

        # Badge escáner TC52
        scan_badge = tk.Frame(center, bg="#0A3020", padx=10, pady=4)
        scan_badge.pack(side="left", padx=8)
        tk.Label(scan_badge, text="📷 TC52 Listo", font=ff(8),
                 bg="#0A3020", fg=C["green_light"]).pack()

        right = tk.Frame(hdr, bg=C["header"])
        right.pack(side="right", padx=20)

        self.lbl_clock = tk.Label(right, text="", font=fm(10),
                                   bg=C["header"], fg=C["green_light"])
        self.lbl_clock.pack(side="right", padx=14)

        tk.Frame(right, bg="#3D6B50", width=1).pack(side="right", fill="y", pady=8)

        user_frame = tk.Frame(right, bg=C["header"])
        user_frame.pack(side="right", padx=12)
        tk.Label(user_frame, text=f"👤  {self.user['name']}", font=ff(9),
                 bg=C["header"], fg=C["header_text"]).pack()
        tk.Label(user_frame, text=self._db_status, font=ff(7),
                 bg=C["header"], fg=C["header_dim"]).pack(anchor="e")

    def _build_body(self):
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        self.left_panel = tk.Frame(body, bg=C["bg"])
        self.left_panel.pack(side="left", fill="both", expand=True)

        tk.Frame(body, bg=C["border"], width=1).pack(side="left", fill="y")

        self.right_panel = tk.Frame(body, bg=C["surface"], width=360)
        self.right_panel.pack(side="right", fill="both")
        self.right_panel.pack_propagate(False)

        self._build_left(self.left_panel)
        self._build_ticket(self.right_panel)

    # ────────────────────────────────────────────────────────────
    #  LEFT PANEL
    # ────────────────────────────────────────────────────────────
    def _build_left(self, parent):
        search_frame = tk.Frame(parent, bg=C["bg"])
        search_frame.pack(fill="x", padx=20, pady=16)

        entry_wrap = tk.Frame(search_frame, bg=C["surface"],
                              highlightthickness=1, highlightbackground=C["border2"])
        entry_wrap.pack(side="left", fill="x", expand=True)

        tk.Label(entry_wrap, text="🔍", font=ff(12), bg=C["surface"],
                 fg=C["text3"]).pack(side="left", padx=(14, 4), pady=8)

        self.entry_search = tk.Entry(
            entry_wrap,
            textvariable=self.search_var,
            font=ff(11),
            bg=C["surface"],
            fg=C["text"],
            insertbackground=C["green"],
            relief="flat",
            bd=0
        )
        self.entry_search.pack(side="left", fill="x", expand=True, pady=10)

        self.entry_search.bind("<FocusIn>",  self._search_focus_in)
        self.entry_search.bind("<FocusOut>", self._search_focus_out)
        self.entry_search.bind("<Return>",   self._on_search_enter)

        scan_icon = tk.Label(search_frame, text="📷", font=ff(14),
                             bg=C["surface"], padx=12, pady=8,
                             cursor="hand2",
                             highlightthickness=1, highlightbackground=C["border2"])
        scan_icon.pack(side="left", padx=(8, 0))
        scan_icon.bind("<Button-1>", lambda e: self._focus_scan_mode())

        # Chips de categorías (dinámicos desde la BD)
        cat_frame = tk.Frame(parent, bg=C["bg"])
        cat_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.cat_buttons = {}
        cat_icons = {
            "Todos": "", "Abarrotes": "🌾", "Bebidas": "🥤", "Lácteos": "🥛",
            "Limpieza": "🧹", "Botanas": "🍿", "Panadería": "🥖",
            "Carnes frías": "🥩", "Higiene": "🧼", "Otros": "📦",
            # Para datos mock:
            "Quesos": "🧀", "Vinos": "🍷", "Dulces": "🍬", "Aceites": "🫒",
        }
        for cat in self._categories:
            icon  = cat_icons.get(cat, "")
            label = f"{icon} {cat}".strip() if icon else cat
            btn = tk.Label(cat_frame, text=label, font=ff(9, "bold"),
                           padx=12, pady=6, cursor="hand2", relief="flat")
            btn.pack(side="left", padx=(0, 6))
            btn.bind("<Button-1>", lambda e, c=cat: self._select_category(c))
            self.cat_buttons[cat] = btn

        self._update_cat_buttons()

        grid_frame = tk.Frame(parent, bg=C["bg"])
        grid_frame.pack(fill="both", expand=True, padx=20)

        self.prod_canvas = tk.Canvas(grid_frame, bg=C["bg"], highlightthickness=0)
        scroll_y = tk.Scrollbar(grid_frame, orient="vertical",
                                command=self.prod_canvas.yview,
                                bg=C["border"], troughcolor=C["bg"])
        scroll_y.pack(side="right", fill="y")
        self.prod_canvas.pack(side="left", fill="both", expand=True)
        self.prod_canvas.configure(yscrollcommand=scroll_y.set)

        self.prod_inner = tk.Frame(self.prod_canvas, bg=C["bg"])
        self._prod_window = self.prod_canvas.create_window((0, 0), window=self.prod_inner, anchor="nw")

        self.prod_inner.bind("<Configure>", lambda e: self.prod_canvas.configure(
            scrollregion=self.prod_canvas.bbox("all")))
        self.prod_canvas.bind("<Configure>", lambda e: self.prod_canvas.itemconfig(
            self._prod_window, width=e.width))
        self.prod_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _focus_scan_mode(self):
        self.search_var.set("")
        self.entry_search.focus_set()
        Toast(self, "Modo escáner activo", "success", 1200)

    def _search_focus_in(self, e):
        self.entry_search.master.config(highlightbackground=C["green_mid"],
                                        highlightthickness=2)

    def _search_focus_out(self, e):
        self.entry_search.master.config(highlightbackground=C["border2"],
                                        highlightthickness=1)

    def _select_category(self, cat):
        self.active_category.set(cat)
        self._update_cat_buttons()
        self._load_products()

    def _update_cat_buttons(self):
        for cat, btn in self.cat_buttons.items():
            if cat == self.active_category.get():
                btn.config(bg=C["green"], fg="white")
            else:
                btn.config(bg=C["surface"], fg=C["text2"])

    # ────────────────────────────────────────────────────────────
    #  PRODUCT CARDS GRID
    # ────────────────────────────────────────────────────────────
    def _render_products(self, products):
        for w in self.prod_inner.winfo_children():
            w.destroy()

        if not products:
            tk.Label(self.prod_inner, text="Sin resultados",
                     font=ff(12), bg=C["bg"], fg=C["text3"],
                     pady=60).pack()
            return

        COLS = 4
        for i, p in enumerate(products):
            row = i // COLS
            col = i % COLS
            self._make_card(p, row, col)

        for c in range(COLS):
            self.prod_inner.columnconfigure(c, weight=1, uniform="col")

    def _make_card(self, p, row, col):
        # Soporta tanto campo 'stock_actual' (BD real) como 'stock_actual' (mock)
        stock    = p.get("stock_actual", p.get("stock_actual", 0))
        is_out   = stock <= 0
        is_low   = 0 < stock <= p.get("stock_minimo", 5)
        # emoji: puede ser un emoji directo o una URL de imagen
        raw_emoji = p.get("emoji", p.get("imagen_url", "📦"))
        emoji     = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"

        card = tk.Frame(
            self.prod_inner,
            bg=C["surface"],
            cursor="hand2" if not is_out else "arrow",
            highlightthickness=1,
            highlightbackground=C["border"]
        )
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        inner = tk.Frame(card, bg=C["surface"], padx=14, pady=12)
        inner.pack(fill="both", expand=True)

        badge_row = tk.Frame(inner, bg=C["surface"])
        badge_row.pack(fill="x")

        emoji_lbl = tk.Label(badge_row, text=emoji, font=ff(22), bg=C["surface"])
        emoji_lbl.pack(side="left")

        if is_out:
            badge = tk.Label(badge_row, text="Agotado", font=ff(7, "bold"),
                             bg=C["chip_red"], fg=C["red"], padx=6, pady=2)
            badge.pack(side="right", anchor="n")
        elif is_low:
            badge = tk.Label(badge_row, text=f"Quedan {stock}", font=ff(7, "bold"),
                             bg=C["chip_amber"], fg=C["amber"], padx=6, pady=2)
            badge.pack(side="right", anchor="n")
        else:
            badge = tk.Label(badge_row, text=f"{stock} disp.", font=ff(7),
                             bg=C["surface"], fg=C["text3"])
            badge.pack(side="right", anchor="n")

        # SKU / código de barras
        sku_text = p.get("codigo_barras", "")
        tk.Label(inner, text=sku_text or "", font=fm(8),
                 bg=C["surface"], fg=C["text3"], anchor="w").pack(fill="x", pady=(6, 0))

        name_lbl = tk.Label(inner, text=p["nombre"], font=ff(10, "bold"),
                            bg=C["surface"], fg=C["text"] if not is_out else C["text3"],
                            anchor="w", wraplength=160, justify="left")
        name_lbl.pack(fill="x")

        price_frame = tk.Frame(inner, bg=C["surface"])
        price_frame.pack(fill="x", pady=(8, 0))

        price = float(p.get("precio_venta", p.get("precio_venta", 0)))
        price_lbl = tk.Label(price_frame, text=f"${price:,.2f}",
                             font=ff(13, "bold"), bg=C["surface"],
                             fg=C["green"] if not is_out else C["text3"])
        price_lbl.pack(side="left")

        # Categoría como sub-etiqueta
        cat_text = p.get("categoria", "")
        tk.Label(price_frame, text=cat_text, font=ff(7),
                 bg=C["surface"], fg=C["text3"]).pack(side="right", pady=(3, 0))

        def on_enter(e, c=card):
            if not is_out:
                c.config(highlightbackground=C["green_mid"], highlightthickness=2)

        def on_leave(e, c=card):
            c.config(highlightbackground=C["border"], highlightthickness=1)

        def on_click(e, prod=p):
            if not is_out:
                self._add_to_cart(prod)

        for widget in [card, inner, badge_row, emoji_lbl, name_lbl, price_lbl, price_frame]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    # ────────────────────────────────────────────────────────────
    #  TICKET (panel derecho)
    # ────────────────────────────────────────────────────────────
    def _build_ticket(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Fila 0: Header
        t_header = tk.Frame(parent, bg=C["surface"])
        t_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 0))

        tk.Label(t_header, text="Ticket", font=ff(16, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")

        clear_btn = tk.Label(t_header, text="🗑 Limpiar", font=ff(8),
                             bg=C["bg2"], fg=C["text2"], padx=8, pady=4, cursor="hand2")
        clear_btn.pack(side="right", padx=(4, 0))
        clear_btn.bind("<Button-1>", lambda e: self._clear_cart())

        self.lbl_items_count = tk.Label(t_header, text="",
                                         font=ff(8, "bold"),
                                         bg=C["green_pale"], fg=C["green"],
                                         padx=8, pady=3)
        self.lbl_items_count.pack(side="right")

        tk.Frame(parent, bg=C["border"], height=1).grid(row=0, column=0, sticky="ews",
                                                         padx=0, pady=(48, 0))

        # Fila 1: Carrito scrollable
        cart_wrap = tk.Frame(parent, bg=C["surface"])
        cart_wrap.grid(row=1, column=0, sticky="nsew")

        self.cart_canvas = tk.Canvas(cart_wrap, bg=C["surface"], highlightthickness=0)
        cart_scroll = tk.Scrollbar(cart_wrap, orient="vertical",
                                   command=self.cart_canvas.yview)
        cart_scroll.pack(side="right", fill="y")
        self.cart_canvas.pack(side="left", fill="both", expand=True)
        self.cart_canvas.configure(yscrollcommand=cart_scroll.set)

        self.cart_inner = tk.Frame(self.cart_canvas, bg=C["surface"])
        self._cart_window = self.cart_canvas.create_window((0, 0), window=self.cart_inner,
                                                            anchor="nw")
        self.cart_inner.bind("<Configure>", lambda e: self.cart_canvas.configure(
            scrollregion=self.cart_canvas.bbox("all")))
        self.cart_canvas.bind("<Configure>", lambda e: self.cart_canvas.itemconfig(
            self._cart_window, width=e.width))

        # Fila 2: Pie (totales + pago + cobrar)
        pie = tk.Frame(parent, bg=C["surface"])
        pie.grid(row=2, column=0, sticky="ew")

        tk.Frame(pie, bg=C["border"], height=1).pack(fill="x")

        totals_inner = tk.Frame(pie, bg=C["surface"], padx=20, pady=12)
        totals_inner.pack(fill="x")

        r_sub = tk.Frame(totals_inner, bg=C["surface"])
        r_sub.pack(fill="x", pady=2)
        tk.Label(r_sub, text="Subtotal", font=ff(9),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")
        self.lbl_subtotal = tk.Label(r_sub, text="$0.00", font=fm(9),
                                      bg=C["surface"], fg=C["text2"])
        self.lbl_subtotal.pack(side="right")

        r_tax = tk.Frame(totals_inner, bg=C["surface"])
        r_tax.pack(fill="x", pady=2)
        tk.Label(r_tax, text="IVA 16%", font=ff(9),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")
        self.lbl_tax = tk.Label(r_tax, text="$0.00", font=fm(9),
                                 bg=C["surface"], fg=C["text2"])
        self.lbl_tax.pack(side="right")

        tk.Frame(totals_inner, bg=C["border"], height=1).pack(fill="x", pady=8)

        r_total = tk.Frame(totals_inner, bg=C["surface"])
        r_total.pack(fill="x")
        tk.Label(r_total, text="TOTAL", font=ff(12, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        self.lbl_total = tk.Label(r_total, text="$0.00", font=fm(20, "bold"),
                                   bg=C["surface"], fg=C["text"])
        self.lbl_total.pack(side="right")

        # Método de pago
        pay_frame = tk.Frame(pie, bg=C["surface"], padx=20, pady=8)
        pay_frame.pack(fill="x")

        self.btn_efectivo = tk.Label(pay_frame, text="💵  Efectivo",
                                      font=ff(9, "bold"), padx=20, pady=8,
                                      cursor="hand2", relief="flat")
        self.btn_efectivo.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_tarjeta = tk.Label(pay_frame, text="💳  Tarjeta",
                                     font=ff(9, "bold"), padx=20, pady=8,
                                     cursor="hand2", relief="flat")
        self.btn_tarjeta.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.btn_efectivo.bind("<Button-1>", lambda e: self._set_payment("efectivo"))
        self.btn_tarjeta.bind("<Button-1>",  lambda e: self._set_payment("tarjeta"))
        self._update_pay_btns()

        # Botón Cobrar
        btn_area = tk.Frame(pie, bg=C["surface"])
        btn_area.pack(fill="x", padx=20, pady=(4, 16))

        self.btn_cobrar_canvas = tk.Canvas(btn_area, bg=C["surface"],
                                           height=50, highlightthickness=0)
        self.btn_cobrar_canvas.pack(fill="x")

        self.btn_cobrar_canvas.bind("<Button-1>", lambda e: self._process_sale()
                                    if getattr(self, "_last_cobrar_enabled", False) else None)
        self.btn_cobrar_canvas.bind("<Configure>", lambda e: self._draw_cobrar_btn(
            getattr(self, "_last_cobrar_text", "$0.00"),
            enabled=getattr(self, "_last_cobrar_enabled", False)
        ))
        self._last_cobrar_text    = "$0.00"
        self._last_cobrar_enabled = False

        # Atajos de teclado
        self.bind_all("<F1>", lambda e: self.entry_search.focus_set())
        self.bind_all("<F2>", lambda e: self._process_sale())
        self.bind_all("<F3>", lambda e: self._clear_cart())
        self.bind_all("<Escape>", lambda e: (self.search_var.set(""),
                                              self.entry_search.focus_set()))

    def _draw_cobrar_btn(self, amount_text, enabled=True):
        self._last_cobrar_text    = amount_text
        self._last_cobrar_enabled = enabled
        c = self.btn_cobrar_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 10:
            return
        h = 50
        r = 10
        fill = C["green"] if enabled else C["text3"]
        c.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=fill, outline=fill)
        c.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=fill, outline=fill)
        c.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=fill, outline=fill)
        c.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=fill, outline=fill)
        c.create_rectangle(r, 0, w-r, h, fill=fill, outline=fill)
        c.create_rectangle(0, r, w, h-r, fill=fill, outline=fill)
        text = f"⊙  Cobrar {amount_text}" if enabled else "⊙  Cobrar $0.00"
        c.create_text(w//2, h//2, text=text, fill="white",
                      font=(F, 12, "bold"), anchor="center")
        c.config(cursor="hand2" if enabled else "arrow")

    def _set_payment(self, method):
        self.pay_var.set(method)
        self._update_pay_btns()

    def _update_pay_btns(self):
        sel = self.pay_var.get()
        if sel == "efectivo":
            self.btn_efectivo.config(bg=C["green"], fg="white")
            self.btn_tarjeta.config(bg=C["bg2"], fg=C["text2"])
        else:
            self.btn_tarjeta.config(bg=C["green"], fg="white")
            self.btn_efectivo.config(bg=C["bg2"], fg=C["text2"])

    # ────────────────────────────────────────────────────────────
    #  RENDER CART
    # ────────────────────────────────────────────────────────────
    def _render_cart(self):
        for w in self.cart_inner.winfo_children():
            w.destroy()

        if not self.cart:
            empty_frame = tk.Frame(self.cart_inner, bg=C["surface"])
            empty_frame.pack(fill="both", expand=True, padx=20, pady=60)
            tk.Label(empty_frame, text="🛒", font=ff(36),
                     bg=C["surface"], fg=C["text3"]).pack()
            tk.Label(empty_frame, text="Ticket vacío", font=ff(12, "bold"),
                     bg=C["surface"], fg=C["text3"]).pack(pady=(8, 4))
            tk.Label(empty_frame, text="Escanea un código o agrega productos",
                     font=ff(9), bg=C["surface"], fg=C["text3"],
                     wraplength=200, justify="center").pack()
            return

        for i, item in enumerate(self.cart):
            p = item["product"]
            item_frame = tk.Frame(self.cart_inner, bg=C["surface"], padx=16, pady=10)
            item_frame.pack(fill="x")

            r1 = tk.Frame(item_frame, bg=C["surface"])
            r1.pack(fill="x")

            raw_emoji = p.get("emoji", p.get("imagen_url", "📦"))
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            tk.Label(r1, text=emoji, font=ff(14), bg=C["surface"]).pack(side="left", padx=(0, 8))

            info = tk.Frame(r1, bg=C["surface"])
            info.pack(side="left", fill="x", expand=True)

            nombre = p.get("nombre", p.get("nombre", ""))
            name_truncated = nombre[:22] + "…" if len(nombre) > 22 else nombre
            tk.Label(info, text=name_truncated, font=ff(9, "bold"),
                     bg=C["surface"], fg=C["text"], anchor="w").pack(fill="x")

            price = float(p.get("precio_venta", 0))
            sku   = p.get("codigo_barras", "")
            price_row = tk.Frame(info, bg=C["surface"])
            price_row.pack(fill="x")
            tk.Label(price_row, text=f"${price:,.2f}", font=fm(8),
                     bg=C["surface"], fg=C["text2"]).pack(side="left")
            tk.Label(price_row, text=f"c/u · {sku}", font=ff(7),
                     bg=C["surface"], fg=C["text3"]).pack(side="left", padx=4)

            tk.Label(r1, text=f"${item['subtotal']:,.2f}",
                     font=fm(10, "bold"), bg=C["surface"], fg=C["text"]).pack(side="right")

            r2 = tk.Frame(item_frame, bg=C["surface"])
            r2.pack(fill="x", pady=(6, 0))

            del_btn = tk.Label(r2, text="Eliminar", font=ff(8),
                               bg=C["surface"], fg=C["text3"], cursor="hand2")
            del_btn.pack(side="left")
            del_btn.bind("<Button-1>", lambda e, idx=i: self._remove_item(idx))

            ctrl = tk.Frame(r2, bg=C["bg2"])
            ctrl.pack(side="right")

            minus = tk.Label(ctrl, text=" − ", font=ff(11, "bold"),
                             bg=C["bg2"], fg=C["text"], cursor="hand2", pady=2)
            minus.pack(side="left")
            minus.bind("<Button-1>", lambda e, idx=i: self._change_qty(idx, -1))

            tk.Label(ctrl, text=f"  {item['qty']}  ", font=fm(10, "bold"),
                     bg=C["bg2"], fg=C["text"]).pack(side="left")

            plus = tk.Label(ctrl, text=" + ", font=ff(11, "bold"),
                            bg=C["bg2"], fg=C["green"], cursor="hand2", pady=2)
            plus.pack(side="left")
            plus.bind("<Button-1>", lambda e, idx=i: self._change_qty(idx, 1))

            if i < len(self.cart) - 1:
                tk.Frame(self.cart_inner, bg=C["border"], height=1).pack(fill="x", padx=16)

        self.cart_canvas.update_idletasks()
        self.cart_canvas.yview_moveto(1.0)

    def _update_totals(self):
        try:
            subtotal = float(sum(float(i["subtotal"]) for i in self.cart))
            tax      = round(subtotal * 0.16, 2)
            total    = round(subtotal + tax, 2)
            count    = sum(int(i["qty"]) for i in self.cart)

            self.lbl_subtotal.config(text=f"${subtotal:,.2f}")
            self.lbl_tax.config(text=f"${tax:,.2f}")
            self.lbl_total.config(text=f"${total:,.2f}")
            self.lbl_items_count.config(text=f"{count} artículos" if count > 0 else "")

            total_str = f"${total:,.2f}"
            self._last_cobrar_text    = total_str
            self._last_cobrar_enabled = bool(self.cart)
            self.after(20, lambda ts=total_str, hc=bool(self.cart):
                       self._draw_cobrar_btn(ts, enabled=hc))
        except Exception as e:
            import traceback
            print(f"[_update_totals ERROR] {e}")
            traceback.print_exc()

    # ────────────────────────────────────────────────────────────
    #  CART OPERATIONS
    # ────────────────────────────────────────────────────────────
    def _add_to_cart(self, product):
        stock_actual = self.db.get_stock(product["id"])
        if stock_actual <= 0:
            Toast(self, f"{product['nombre']} está agotado", "error")
            return

        existing = next((i for i in self.cart if i["product"]["id"] == product["id"]), None)
        if existing:
            if existing["qty"] >= stock_actual:
                Toast(self, f"Solo hay {stock_actual} disponibles", "warning")
                return
            existing["qty"] += 1
            existing["subtotal"] = float(existing["qty"]) * float(existing["product"]["precio_venta"])
        else:
            self.cart.append({
                "product": product,
                "qty": 1,
                "subtotal": float(product["precio_venta"])
            })

        self._render_cart()
        self._update_totals()
        Toast(self, f"+ {product['nombre']}", "success", 1200)

    def _change_qty(self, idx, delta):
        item = self.cart[idx]
        new_qty = item["qty"] + delta
        if new_qty <= 0:
            self._remove_item(idx)
            return
        stock_actual = self.db.get_stock(item["product"]["id"])
        if new_qty > stock_actual:
            Toast(self, f"Solo hay {stock_actual} disponibles", "warning")
            return
        item["qty"] = new_qty
        item["subtotal"] = float(new_qty) * float(item["product"]["precio_venta"])
        self._render_cart()
        self._update_totals()

    def _remove_item(self, idx):
        name = self.cart[idx]["product"]["nombre"]
        self.cart.pop(idx)
        self._render_cart()
        self._update_totals()
        Toast(self, f"Eliminado: {name[:20]}", "warning", 1200)

    def _clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Limpiar ticket",
                               "¿Cancelar todos los artículos del ticket actual?"):
            self.cart.clear()
            self._render_cart()
            self._update_totals()

    # ────────────────────────────────────────────────────────────
    #  PROCESO DE VENTA
    # ────────────────────────────────────────────────────────────
    def _process_sale(self):
        if not self.cart:
            return

        subtotal = sum(i["subtotal"] for i in self.cart)
        tax      = subtotal * 0.16
        total    = subtotal + tax
        payment  = self.pay_var.get()

        FOLIO_COUNTER[0] += 1
        folio = f"CAJA-{FOLIO_COUNTER[0]:06d}"

        # Snapshot antes de limpiar
        cart_snapshot = [dict(i) for i in self.cart]

        # ── Guardar en BD (usa registrar_venta() — atómico) ─────
        venta_id, error = self.db.save_sale(
            folio, self.cart, total, subtotal, tax,
            payment, self.user["name"], self.location["name"],
            usuario_id=self.user.get("id") if isinstance(self.user.get("id"), int) else None
        )

        if error and error != "sin_conexion":
            # Error de negocio (stock insuficiente, producto no encontrado, etc.)
            messagebox.showerror(
                "Error en la venta",
                f"No se pudo completar la venta:\n{error}"
            )
            # Revertir el folio y no limpiar el carrito
            FOLIO_COUNTER[0] -= 1
            return

        # ── Limpiar ticket ───────────────────────────────────────
        self.cart.clear()
        self._render_cart()
        self._update_totals()
        self._load_products()   # refresca stock en pantalla

        # ── Mostrar modal de cobro ───────────────────────────────
        if payment == "tarjeta":
            self._show_card_modal(folio, total, subtotal, tax, cart_snapshot)
        else:
            self._show_cash_modal(folio, total, subtotal, tax, cart_snapshot)

    def _reset_for_new_sale(self):
        self.search_var.set("")
        self.active_category.set("Todos")
        self._update_cat_buttons()
        self._load_products()
        self.entry_search.focus_set()

    # ════════════════════════════════════════════════════════════
    #  MODAL EFECTIVO
    # ════════════════════════════════════════════════════════════
    def _show_cash_modal(self, folio, total, subtotal, tax, cart_snapshot):
        dlg = tk.Toplevel(self)
        dlg.title("Cobro en Efectivo")
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 460, 640
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg=C["green"], pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💵", font=ff(32), bg=C["green"]).pack()
        tk.Label(hdr, text="Cobro en Efectivo", font=ff(14, "bold"),
                 bg=C["green"], fg="white").pack(pady=(4, 0))
        tk.Label(hdr, text=f"Ticket {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}",
                 font=ff(8), bg=C["green"], fg=C["green_light"]).pack()

        body = tk.Frame(dlg, bg=C["surface"])
        body.pack(fill="both", expand=True, padx=28, pady=16)

        items_bg = tk.Frame(body, bg=C["bg2"], pady=2)
        items_bg.pack(fill="x", pady=(0, 12))
        for item in cart_snapshot:
            r = tk.Frame(items_bg, bg=C["bg2"])
            r.pack(fill="x", padx=12, pady=2)
            nombre = item["product"].get("nombre", "")
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(9), bg=C["bg2"],
                     fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        t_row = tk.Frame(body, bg=C["surface"])
        t_row.pack(fill="x")
        for lbl, val in [("Subtotal", f"${subtotal:,.2f}"), ("IVA 16%", f"${tax:,.2f}")]:
            r = tk.Frame(t_row, bg=C["surface"])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=lbl, font=ff(9), bg=C["surface"], fg=C["text2"]).pack(side="left")
            tk.Label(r, text=val, font=fm(9), bg=C["surface"], fg=C["text2"]).pack(side="right")
        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=6)
        r_t = tk.Frame(body, bg=C["surface"])
        r_t.pack(fill="x")
        tk.Label(r_t, text="TOTAL", font=ff(13, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        tk.Label(r_t, text=f"${total:,.2f}", font=fm(16, "bold"),
                 bg=C["surface"], fg=C["green"]).pack(side="right")

        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=10)

        tk.Label(body, text="Con cuánto paga el cliente:", font=ff(9, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w")

        cash_wrap = tk.Frame(body, bg=C["surface"],
                             highlightthickness=2, highlightbackground=C["green_mid"])
        cash_wrap.pack(fill="x", pady=(4, 0))
        tk.Label(cash_wrap, text="$", font=fm(16, "bold"),
                 bg=C["surface"], fg=C["text2"], padx=8).pack(side="left")
        cash_var = tk.StringVar()
        entry_cash = tk.Entry(cash_wrap, textvariable=cash_var,
                              font=fm(16, "bold"), bg=C["surface"],
                              fg=C["text"], insertbackground=C["green"],
                              relief="flat", bd=0, width=12, justify="right")
        entry_cash.pack(side="left", fill="x", expand=True, pady=12, padx=(0, 12))
        entry_cash.focus_set()

        change_frame = tk.Frame(body, bg=C["surface"])
        change_frame.pack(fill="x", pady=6)
        tk.Label(change_frame, text="Cambio:", font=ff(11, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")
        lbl_change = tk.Label(change_frame, text="—", font=fm(16, "bold"),
                              bg=C["surface"], fg=C["text3"])
        lbl_change.pack(side="right")

        quick_frame = tk.Frame(body, bg=C["surface"])
        quick_frame.pack(fill="x", pady=(4, 10))
        tk.Label(quick_frame, text="Rápidos:", font=ff(8),
                 bg=C["surface"], fg=C["text3"]).pack(side="left", padx=(0, 8))

        def set_amount(amt):
            cash_var.set(f"{amt:.0f}")
            _recalc()

        suggestions = []
        for bill in [20, 50, 100, 200, 500, 1000]:
            if bill >= total:
                suggestions.append(bill)
                if len(suggestions) == 4:
                    break
        if not suggestions:
            suggestions = [500, 1000]

        for amt in suggestions:
            b = tk.Label(quick_frame, text=f"${int(amt):,}", font=ff(9, "bold"),
                         bg=C["bg2"], fg=C["text"], padx=10, pady=4,
                         cursor="hand2", relief="flat")
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, a=amt: set_amount(a))

        def _recalc(*args):
            try:
                paid = float(cash_var.get().replace(",", ""))
                cambio = paid - total
                if cambio < 0:
                    lbl_change.config(text=f"-${abs(cambio):,.2f}", fg=C["red"])
                    btn_confirm.config(state="disabled", bg=C["text3"])
                else:
                    lbl_change.config(text=f"${cambio:,.2f}", fg=C["green"])
                    btn_confirm.config(state="normal", bg=C["green"])
            except ValueError:
                lbl_change.config(text="—", fg=C["text3"])
                btn_confirm.config(state="disabled", bg=C["text3"])

        cash_var.trace_add("write", _recalc)
        entry_cash.bind("<Return>", lambda e: _confirm_cash())

        def _confirm_cash():
            try:
                paid = float(cash_var.get().replace(",", ""))
                if paid < total:
                    return
            except:
                return
            cambio_val = paid - total
            dlg.destroy()
            self._show_cash_success(folio, total, subtotal, tax,
                                    cart_snapshot, paid, cambio_val)

        btn_confirm = tk.Button(body, text="✓  Confirmar cobro",
                                font=ff(12, "bold"),
                                bg=C["text3"], fg="white",
                                activebackground=C["green_hover"],
                                relief="flat", bd=0, cursor="hand2",
                                state="disabled",
                                command=_confirm_cash)
        btn_confirm.pack(fill="x", ipady=13, pady=(6, 4))

        btn_cancel = tk.Button(body, text="Cancelar",
                               font=ff(9), bg=C["surface"], fg=C["text3"],
                               activebackground=C["bg2"],
                               relief="flat", bd=0, cursor="hand2",
                               command=lambda: [dlg.destroy(), self._reset_for_new_sale()])
        btn_cancel.pack(fill="x", ipady=6)

        dlg.bind("<Escape>", lambda e: [dlg.destroy(), self._reset_for_new_sale()])

    # ════════════════════════════════════════════════════════════
    #  MODAL ÉXITO EFECTIVO
    # ════════════════════════════════════════════════════════════
    def _show_cash_success(self, folio, total, subtotal, tax,
                           cart_snapshot, paid, cambio):
        dlg = tk.Toplevel(self)
        dlg.title("¡Venta Exitosa!")
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 420, 540
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg=C["surface"])
        hdr.pack(fill="x", padx=24, pady=16)
        tk.Label(hdr, text="¡Listo!", font=ff(18, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")

        chk_bg = tk.Frame(dlg, bg=C["green_pale"], width=72, height=72)
        chk_bg.pack()
        chk_bg.pack_propagate(False)
        tk.Label(chk_bg, text="✓", font=ff(28, "bold"),
                 bg=C["green_pale"], fg=C["green"]).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(dlg, text="¡Venta Exitosa!", font=ff(15, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(pady=(8, 2))
        tk.Label(dlg,
                 text=f"Ticket {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}",
                 font=ff(8), bg=C["surface"], fg=C["text3"]).pack()

        cambio_frame = tk.Frame(dlg, bg=C["green_pale"], pady=14)
        cambio_frame.pack(fill="x", padx=24, pady=12)
        tk.Label(cambio_frame, text="CAMBIO", font=ff(10, "bold"),
                 bg=C["green_pale"], fg=C["green_mid"]).pack()
        tk.Label(cambio_frame, text=f"${cambio:,.2f}", font=fm(26, "bold"),
                 bg=C["green_pale"], fg=C["green"]).pack()
        tk.Label(cambio_frame,
                 text=f"  Recibido: ${paid:,.2f}  ·  Total: ${total:,.2f}  ",
                 font=ff(8), bg=C["green_pale"], fg=C["green_mid"]).pack()

        items_bg = tk.Frame(dlg, bg=C["bg2"])
        items_bg.pack(fill="x", padx=24, pady=(0, 8))
        items_inner = tk.Frame(items_bg, bg=C["bg2"], padx=12, pady=8)
        items_inner.pack(fill="x")
        for item in cart_snapshot:
            r = tk.Frame(items_inner, bg=C["bg2"])
            r.pack(fill="x", pady=1)
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            nombre = item["product"].get("nombre", "")
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(9), bg=C["bg2"],
                     fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        btn_row = tk.Frame(dlg, bg=C["surface"])
        btn_row.pack(fill="x", padx=24, pady=(0, 4))
        tk.Button(btn_row, text="🖨  Imprimir", font=ff(9),
                  bg=C["surface"], fg=C["text"], relief="solid", bd=1,
                  padx=12, pady=7, cursor="hand2").pack(side="left", fill="x",
                                                         expand=True, padx=(0, 5))
        tk.Button(btn_row, text="📧  Enviar", font=ff(9),
                  bg=C["surface"], fg=C["text"], relief="solid", bd=1,
                  padx=12, pady=7, cursor="hand2").pack(side="left", fill="x", expand=True)

        def close_and_reset():
            dlg.destroy()
            self._reset_for_new_sale()

        nueva_btn = tk.Button(dlg, text="Nueva Venta",
                              font=ff(12, "bold"),
                              bg=C["green"], fg="white",
                              activebackground=C["green_hover"],
                              relief="flat", bd=0, cursor="hand2",
                              command=close_and_reset)
        nueva_btn.pack(fill="x", padx=24, pady=(4, 20), ipady=12)
        nueva_btn.focus_set()

        dlg.bind("<Return>", lambda e: close_and_reset())
        dlg.bind("<Escape>", lambda e: close_and_reset())
        dlg.after(30000, lambda: (dlg.destroy(), self._reset_for_new_sale())
                  if dlg.winfo_exists() else None)

    # ════════════════════════════════════════════════════════════
    #  MODAL TARJETA
    # ════════════════════════════════════════════════════════════
    def _show_card_modal(self, folio, total, subtotal, tax, cart_snapshot):
        dlg = tk.Toplevel(self)
        dlg.title("Cobro con Tarjeta")
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 440, 560
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg="#1A2B4A", pady=20)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💳", font=ff(32), bg="#1A2B4A").pack()
        tk.Label(hdr, text="Cobro con Tarjeta", font=ff(14, "bold"),
                 bg="#1A2B4A", fg="white").pack(pady=(4, 0))
        tk.Label(hdr,
                 text=f"Ticket {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}",
                 font=ff(8), bg="#1A2B4A", fg="#7A9CC0").pack()

        body = tk.Frame(dlg, bg=C["surface"])
        body.pack(fill="both", expand=True, padx=28, pady=16)

        total_frame = tk.Frame(body, bg=C["surface"])
        total_frame.pack(pady=(0, 12))
        tk.Label(total_frame, text="Total a cobrar", font=ff(10),
                 bg=C["surface"], fg=C["text2"]).pack()
        tk.Label(total_frame, text=f"${total:,.2f}", font=fm(24, "bold"),
                 bg=C["surface"], fg="#1A2B4A").pack()

        terminal_frame = tk.Frame(body, bg="#F0F4FA", pady=16)
        terminal_frame.pack(fill="x", pady=(0, 12))
        tk.Label(terminal_frame, text="⬛", font=ff(28),
                 bg="#F0F4FA", fg="#333").pack()
        tk.Label(terminal_frame, text="Pointer  ·  Terminal no conectada",
                 font=ff(9, "bold"), bg="#F0F4FA", fg="#1A2B4A").pack(pady=(6, 2))
        lbl_status = tk.Label(terminal_frame,
                               text="⚠  Integración pendiente — confirma manualmente",
                               font=ff(8), bg="#F0F4FA", fg=C["amber"])
        lbl_status.pack()

        prog_outer = tk.Frame(body, bg=C["border"], height=4)
        prog_outer.pack(fill="x", pady=4)
        prog_bar = tk.Frame(prog_outer, bg="#1A2B4A", height=4, width=0)
        prog_bar.place(x=0, y=0, relheight=1)

        items_bg = tk.Frame(body, bg=C["bg2"], pady=2)
        items_bg.pack(fill="x", pady=(8, 0))
        for item in cart_snapshot:
            r = tk.Frame(items_bg, bg=C["bg2"])
            r.pack(fill="x", padx=12, pady=2)
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            nombre = item["product"].get("nombre", "")
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(9), bg=C["bg2"],
                     fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        def _confirm_card():
            dlg.destroy()
            self._show_card_success(folio, total, subtotal, tax, cart_snapshot)

        btn_confirm = tk.Button(body, text="✓  Pago Confirmado (Manual)",
                                font=ff(11, "bold"),
                                bg="#1A2B4A", fg="white",
                                activebackground="#243D6A",
                                relief="flat", bd=0, cursor="hand2",
                                command=_confirm_card)
        btn_confirm.pack(fill="x", ipady=13, pady=(12, 4))

        btn_cancel = tk.Button(body, text="Cancelar transacción",
                               font=ff(9), bg=C["surface"], fg=C["text3"],
                               activebackground=C["bg2"],
                               relief="flat", bd=0, cursor="hand2",
                               command=lambda: [dlg.destroy(), self._reset_for_new_sale()])
        btn_cancel.pack(fill="x", ipady=6)

        def animate(step=0):
            try:
                pct = min(step / 80, 1.0)
                prog_bar.place(x=0, y=0, relheight=1,
                               width=int(prog_outer.winfo_width() * pct))
                if step < 80:
                    dlg.after(60, lambda: animate(step + 1))
                else:
                    lbl_status.config(text="🟡  Esperando respuesta del terminal…",
                                      fg=C["amber"])
            except: pass

        dlg.after(200, animate)
        dlg.bind("<Return>", lambda e: _confirm_card())
        dlg.bind("<Escape>", lambda e: [dlg.destroy(), self._reset_for_new_sale()])

    # ════════════════════════════════════════════════════════════
    #  MODAL ÉXITO TARJETA
    # ════════════════════════════════════════════════════════════
    def _show_card_success(self, folio, total, subtotal, tax, cart_snapshot):
        dlg = tk.Toplevel(self)
        dlg.title("Pago con Tarjeta Exitoso")
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 420, 500
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg=C["surface"])
        hdr.pack(fill="x", padx=24, pady=16)
        tk.Label(hdr, text="¡Listo!", font=ff(18, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")

        chk_bg = tk.Frame(dlg, bg="#EEF2FF", width=72, height=72)
        chk_bg.pack()
        chk_bg.pack_propagate(False)
        tk.Label(chk_bg, text="✓", font=ff(28, "bold"),
                 bg="#EEF2FF", fg="#1A2B4A").place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(dlg, text="Pago con Tarjeta Aprobado", font=ff(15, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(pady=(8, 2))
        tk.Label(dlg,
                 text=f"Ticket {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}",
                 font=ff(8), bg=C["surface"], fg=C["text3"]).pack()

        total_f = tk.Frame(dlg, bg="#EEF2FF", pady=10)
        total_f.pack(fill="x", padx=24, pady=10)
        tk.Label(total_f, text=f"${total:,.2f}", font=fm(22, "bold"),
                 bg="#EEF2FF", fg="#1A2B4A").pack()
        tk.Label(total_f, text="💳  Tarjeta", font=ff(9),
                 bg="#EEF2FF", fg="#4A6A9A").pack()

        items_bg = tk.Frame(dlg, bg=C["bg2"])
        items_bg.pack(fill="x", padx=24, pady=(0, 8))
        items_inner = tk.Frame(items_bg, bg=C["bg2"], padx=12, pady=8)
        items_inner.pack(fill="x")
        for item in cart_snapshot:
            r = tk.Frame(items_inner, bg=C["bg2"])
            r.pack(fill="x", pady=1)
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            nombre = item["product"].get("nombre", "")
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(9), bg=C["bg2"],
                     fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        btn_row = tk.Frame(dlg, bg=C["surface"])
        btn_row.pack(fill="x", padx=24, pady=(0, 4))
        tk.Button(btn_row, text="🖨  Imprimir", font=ff(9),
                  bg=C["surface"], fg=C["text"], relief="solid", bd=1,
                  padx=12, pady=7, cursor="hand2").pack(side="left", fill="x",
                                                         expand=True, padx=(0, 5))
        tk.Button(btn_row, text="📧  Enviar", font=ff(9),
                  bg=C["surface"], fg=C["text"], relief="solid", bd=1,
                  padx=12, pady=7, cursor="hand2").pack(side="left", fill="x", expand=True)

        def close_and_reset():
            dlg.destroy()
            self._reset_for_new_sale()

        nueva_btn = tk.Button(dlg, text="Nueva Venta",
                              font=ff(12, "bold"),
                              bg="#1A2B4A", fg="white",
                              activebackground="#243D6A",
                              relief="flat", bd=0, cursor="hand2",
                              command=close_and_reset)
        nueva_btn.pack(fill="x", padx=24, pady=(4, 20), ipady=12)
        nueva_btn.focus_set()

        dlg.bind("<Return>", lambda e: close_and_reset())
        dlg.bind("<Escape>", lambda e: close_and_reset())
        dlg.after(30000, lambda: (dlg.destroy(), self._reset_for_new_sale())
                  if dlg.winfo_exists() else None)

    # ────────────────────────────────────────────────────────────
    #  DATA LOADING
    # ────────────────────────────────────────────────────────────
    def _load_products(self):
        search   = self.search_var.get().strip()
        category = self.active_category.get()
        products = self.db.get_products(search, category)
        self.products = products
        self._render_products(products)

    def _on_search_change(self, *args):
        if self._search_after:
            self.after_cancel(self._search_after)
        self._search_after = self.after(250, self._load_products)

    def _on_search_enter(self, event):
        q = self.search_var.get().strip()
        if not q:
            return
        visible = self.db.get_products(q, self.active_category.get())
        if len(visible) == 1 and visible[0].get("stock_actual", 0) > 0:
            self._add_to_cart(visible[0])
            self.search_var.set("")

    def _on_mousewheel(self, event):
        try:
            self.prod_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except: pass

    # ────────────────────────────────────────────────────────────
    #  CLOCK
    # ────────────────────────────────────────────────────────────
    def _start_clock(self):
        def tick():
            while True:
                now = datetime.now().strftime("%a %d %b  %I:%M %p")
                try:
                    self.lbl_clock.config(text=now)
                except:
                    break
                time.sleep(30)
        threading.Thread(target=tick, daemon=True).start()
        self.lbl_clock.config(text=datetime.now().strftime("%a %d %b  %I:%M %p"))

    def on_close(self):
        self.db.close()
        self.destroy()


# ════════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ════════════════════════════════════════════════════════════════
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("La Casita — Inicio de Sesión")
        self.resizable(False, False)
        self.configure(bg=C["header"])
        self._logged_user = None

        w, h = 420, 520
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self._build()

    def _build(self):
        top_bg = tk.Frame(self, bg=C["header"], height=180)
        top_bg.pack(fill="x")
        top_bg.pack_propagate(False)

        logo_outer = tk.Frame(top_bg, bg="#2A5240", width=72, height=72)
        logo_outer.place(relx=0.5, rely=0.42, anchor="center")
        logo_outer.pack_propagate(False)
        tk.Label(logo_outer, text="LC", font=ff(22, "bold"),
                 bg="#2A5240", fg="white").place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(top_bg, text="La Casita", font=ff(18, "bold"),
                 bg=C["header"], fg=C["header_text"]).place(relx=0.5, rely=0.72, anchor="center")
        tk.Label(top_bg, text="Caja", font=ff(8),
                 bg=C["header"], fg=C["header_dim"]).place(relx=0.5, rely=0.88, anchor="center")

        card = tk.Frame(self, bg=C["surface"], padx=36, pady=32)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Iniciar sesión", font=ff(15, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(card, text="Ingresa tus credenciales para continuar",
                 font=ff(9), bg=C["surface"], fg=C["text3"]).pack(anchor="w", pady=(2, 20))

        tk.Label(card, text="Usuario", font=ff(9, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w")
        user_wrap = tk.Frame(card, bg=C["surface"],
                             highlightthickness=1, highlightbackground=C["border2"])
        user_wrap.pack(fill="x", pady=(4, 14))
        self.entry_user = tk.Entry(user_wrap, font=ff(11), bg=C["surface"], fg=C["text"],
                                   insertbackground=C["green"], relief="flat", bd=0)
        self.entry_user.pack(fill="x", padx=12, pady=10)
        self.entry_user.bind("<FocusIn>",
                             lambda e: user_wrap.config(highlightbackground=C["green_mid"], highlightthickness=2))
        self.entry_user.bind("<FocusOut>",
                             lambda e: user_wrap.config(highlightbackground=C["border2"], highlightthickness=1))
        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus_set())

        tk.Label(card, text="Contraseña", font=ff(9, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w")
        pass_wrap = tk.Frame(card, bg=C["surface"],
                             highlightthickness=1, highlightbackground=C["border2"])
        pass_wrap.pack(fill="x", pady=(4, 6))
        self.entry_pass = tk.Entry(pass_wrap, font=ff(11), bg=C["surface"], fg=C["text"],
                                   insertbackground=C["green"], show="●", relief="flat", bd=0)
        self.entry_pass.pack(fill="x", padx=12, pady=10)
        self.entry_pass.bind("<FocusIn>",
                             lambda e: pass_wrap.config(highlightbackground=C["green_mid"], highlightthickness=2))
        self.entry_pass.bind("<FocusOut>",
                             lambda e: pass_wrap.config(highlightbackground=C["border2"], highlightthickness=1))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = tk.Label(card, text="", font=ff(9),
                                   bg=C["surface"], fg=C["red"])
        self.lbl_error.pack(anchor="w", pady=(0, 12))

        login_btn = tk.Button(card, text="Entrar", font=ff(12, "bold"),
                              bg=C["green"], fg="white",
                              activebackground=C["green_hover"],
                              relief="flat", bd=0, cursor="hand2",
                              command=self._do_login)
        login_btn.pack(fill="x", ipady=12)

        tk.Label(card, text="usuario: prueba  ·  contraseña: prueba",
                 font=ff(8), bg=C["surface"], fg=C["text3"]).pack(pady=(14, 0))

        self.entry_user.focus_set()

    def _do_login(self):
        username = self.entry_user.get().strip().lower()
        password = self.entry_pass.get()
        if username in SYSTEM_USERS:
            stored_pass, display_name, db_id = SYSTEM_USERS[username]
            if password == stored_pass:
                self._logged_user = {
                    "id":   db_id,      # puede ser None si no mapeado aún
                    "name": display_name,
                    "role": "cajero"
                }
                self.destroy()
                return
        self.lbl_error.config(text="Usuario o contraseña incorrectos")
        self.entry_pass.delete(0, tk.END)
        self.entry_pass.focus_set()

    def get_user(self):
        return self._logged_user


# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()

    user = login.get_user()
    if not user:
        exit(0)

    app = CajaApp(logged_user=user)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()