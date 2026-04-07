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

# ── PALETA LA CASITA — Editorial Artisanship ────────────────────
C = {
    "bg":           "#fcf9f4",
    "surface":      "#fcf9f4",
    "surface_low":  "#f6f3ee",
    "surface_high": "#ebe8e3",
    "surface_highest": "#e5e2dd",
    "surface_lowest": "#ffffff",
    "on_surface":   "#1c1c19",
    "on_surface_variant": "#414844",
    "primary":      "#012d1d",
    "primary_container": "#1b4332",
    "on_primary":   "#ffffff",
    "on_primary_container": "#86af99",
    "secondary":    "#7b5819",
    "secondary_container": "#fdcd83",
    "on_secondary_container": "#785516",
    "secondary_fixed": "#ffdeae",
    "on_secondary_fixed": "#281900",
    "outline_variant": "#c1c8c2",
    "error":        "#ba1a1a",
    "error_container": "#ffdad6",
    # Mapeo de compatibilidad con código anterior
    "text":         "#1c1c19",
    "text2":        "#414844",
    "text3":        "#717973",
    "green":        "#012d1d",
    "green_mid":    "#3f6653",
    "green_light":  "#a5d0b9",
    "green_pale":   "#f0ede8",
    "amber":        "#7b5819",
    "red":          "#ba1a1a",
    "header":       "#012d1d",
    "header2":      "#1b4332",
    "header_text":  "#ffffff",
    "header_dim":   "#86af99",
    "border":       "#c1c8c2",
    "border2":      "#717973",
    "bg2":          "#f6f3ee",
    "chip_green":   "#c1ecd4",
    "chip_red":     "#ffdad6",
    "chip_amber":   "#ffdeae",
}

F_SANS = "Plus Jakarta Sans"
F_SERIF = "Newsreader"

def ff(size=10, weight="normal"):
    """Sans-serif font (Body/Label)"""
    return (F_SANS, size, weight)

def fh(size=10, weight="normal"):
    """Serif font (Headline)"""
    return (F_SERIF, size, weight)

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
            # Use the new header search entry
            self.hdr_search_entry.config(bg=C["green_light"])
            self.after(300, lambda: self.hdr_search_entry.config(bg=C["primary_container"]))
        else:
            Toast(self, f"Código no encontrado: {code}", "error", 2500)

    # ────────────────────────────────────────────────────────────
    #  BUILD UI
    # ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Layout principal: Sidebar (Izquierda) + Main (Centro + Derecha)
        self._build_sidebar()

        self.main_container = tk.Frame(self, bg=C["bg"])
        self.main_container.pack(side="left", fill="both", expand=True)

        self._build_header(self.main_container)
        self._build_body(self.main_container)

    def _build_sidebar(self):
        # Sidebar Izquierdo: Branding, Navegación y Perfil
        side = tk.Frame(self, bg=C["surface_low"], width=240, padx=20, pady=24)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        # Brand Title
        brand_frame = tk.Frame(side, bg=C["surface_low"])
        brand_frame.pack(fill="x", pady=(0, 32))
        tk.Label(brand_frame, text="La Casita Deli", font=fh(18, "bold italic"),
                 bg=C["surface_low"], fg=C["primary"], anchor="w").pack(fill="x")
        tk.Label(brand_frame, text="ADMIN TERMINAL", font=ff(7, "bold"),
                 bg=C["surface_low"], fg=C["on_surface_variant"], anchor="w").pack(fill="x")

        # Navigation
        nav = tk.Frame(side, bg=C["surface_low"])
        nav.pack(fill="both", expand=True)

        items = [
            ("dashboard", "Dashboard", False),
            ("point_of_sale", "POS", True),
            ("inventory_2", "Inventory", False),
            ("receipt_long", "Orders", False),
            ("settings", "Settings", False),
        ]

        for icon, label, active in items:
            f = tk.Frame(nav, bg=C["primary"] if active else C["surface_low"], padx=12, pady=10)
            f.pack(fill="x", pady=2)

            # Label de icono (usando texto por ahora como placeholder de icono)
            tk.Label(f, text="•", font=ff(10),
                     bg=C["primary"] if active else C["surface_low"],
                     fg="white" if active else C["on_surface_variant"]).pack(side="left", padx=(0, 8))

            tk.Label(f, text=label, font=ff(9, "bold" if active else "normal"),
                     bg=C["primary"] if active else C["surface_low"],
                     fg="white" if active else C["on_surface_variant"]).pack(side="left")

        # Bottom Profile
        profile_box = tk.Frame(side, bg=C["surface_low"], pady=20)
        profile_box.pack(side="bottom", fill="x")

        tk.Frame(profile_box, bg=C["surface_high"], height=1).pack(fill="x", pady=(0, 20))

        user_card = tk.Frame(profile_box, bg=C["surface_high"], padx=12, pady=12)
        user_card.pack(fill="x", pady=(0, 12))

        tk.Label(user_card, text=f"👤 {self.user['name']}", font=ff(9, "bold"),
                 bg=C["surface_high"], fg=C["on_surface"], anchor="w").pack(fill="x")
        tk.Label(user_card, text="Shift Manager", font=ff(7),
                 bg=C["surface_high"], fg=C["on_surface_variant"], anchor="w").pack(fill="x")

        btn_reg = tk.Button(profile_box, text="OPEN REGISTER", font=ff(7, "bold"),
                            bg=C["secondary_container"], fg=C["on_secondary_container"],
                            relief="flat", bd=0, pady=10, cursor="hand2")
        btn_reg.pack(fill="x")

    def _build_header(self, parent):
        hdr = tk.Frame(parent, bg=C["primary"], padx=32, pady=24)
        hdr.pack(fill="x", side="top")

        top_row = tk.Frame(hdr, bg=C["primary"])
        top_row.pack(fill="x", pady=(0, 24))

        left = tk.Frame(top_row, bg=C["primary"])
        left.pack(side="left")
        tk.Label(left, text="Artisanal Market POS", font=fh(18, "italic"),
                 bg=C["primary"], fg="white").pack(anchor="w")
        tk.Label(left, text=f"Transaction #4829 • Station 02 • {self.location['name']}",
                 font=ff(8), bg=C["primary"], fg=C["on_primary_container"]).pack(anchor="w")

        right = tk.Frame(top_row, bg=C["primary"])
        right.pack(side="right")

        # Search bar integration in header
        search_wrap = tk.Frame(right, bg=C["primary_container"], padx=16, pady=8)
        # We will make this more rounded in a later step when we refine search
        search_wrap.pack(side="left", padx=8)

        tk.Label(search_wrap, text="🔍", font=ff(10), bg=C["primary_container"],
                 fg=C["on_primary_container"]).pack(side="left", padx=(0, 8))

        # We'll use the existing search_var, but need to move the entry here
        self.hdr_search_entry = tk.Entry(
            search_wrap,
            textvariable=self.search_var,
            font=ff(10),
            bg=C["primary_container"],
            fg="white",
            insertbackground="white",
            relief="flat",
            bd=0,
            width=25
        )
        self.hdr_search_entry.pack(side="left")

        # Restore bindings for the search entry
        self.hdr_search_entry.bind("<FocusIn>",  self._search_focus_in)
        self.hdr_search_entry.bind("<FocusOut>", self._search_focus_out)
        self.hdr_search_entry.bind("<Return>",   self._on_search_enter)

        # Badge escáner integration
        scan_btn = tk.Frame(right, bg=C["primary_container"], padx=10, pady=8)
        scan_btn.pack(side="left", padx=8)
        tk.Label(scan_btn, text="📷", font=ff(12), bg=C["primary_container"],
                 fg="white").pack()

        # Categories row
        self.cat_frame = tk.Frame(hdr, bg=C["primary"])
        self.cat_frame.pack(fill="x")
        self._update_cat_buttons()

    def _build_body(self, parent):
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True)

        self.left_panel = tk.Frame(body, bg=C["surface_low"]) # Product grid area
        self.left_panel.pack(side="left", fill="both", expand=True)

        # Tonal layering instead of border
        # tk.Frame(body, bg=C["border"], width=1).pack(side="left", fill="y")

        self.right_panel = tk.Frame(body, bg=C["surface_lowest"], width=380) # Ticket
        self.right_panel.pack(side="right", fill="both")
        self.right_panel.pack_propagate(False)

        self._build_left(self.left_panel)
        self._build_ticket(self.right_panel)

    # ────────────────────────────────────────────────────────────
    #  LEFT PANEL
    # ────────────────────────────────────────────────────────────
    def _build_left(self, parent):
        # Already moved search and categories to header, but we still need
        # a placeholder or adjustment to the grid frame.

        grid_frame = tk.Frame(parent, bg=C["surface_low"])
        grid_frame.pack(fill="both", expand=True, padx=32, pady=32)

        self.prod_canvas = tk.Canvas(grid_frame, bg=C["surface_low"], highlightthickness=0)
        scroll_y = tk.Scrollbar(grid_frame, orient="vertical",
                                command=self.prod_canvas.yview,
                                bg=C["surface_low"], troughcolor=C["surface_low"])
        scroll_y.pack(side="right", fill="y")
        self.prod_canvas.pack(side="left", fill="both", expand=True)
        self.prod_canvas.configure(yscrollcommand=scroll_y.set)

        self.prod_inner = tk.Frame(self.prod_canvas, bg=C["surface_low"])
        self._prod_window = self.prod_canvas.create_window((0, 0), window=self.prod_inner, anchor="nw")

        self.prod_inner.bind("<Configure>", lambda e: self.prod_canvas.configure(
            scrollregion=self.prod_canvas.bbox("all")))
        self.prod_canvas.bind("<Configure>", lambda e: self.prod_canvas.itemconfig(
            self._prod_window, width=e.width))
        self.prod_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _focus_scan_mode(self):
        self.search_var.set("")
        self.hdr_search_entry.focus_set()
        Toast(self, "Modo escáner activo", "success", 1200)

    def _search_focus_in(self, e):
        self.hdr_search_entry.master.config(bg=C["green_mid"])

    def _search_focus_out(self, e):
        self.hdr_search_entry.master.config(bg=C["primary_container"])

    def _select_category(self, cat):
        self.active_category.set(cat)
        self._update_cat_buttons()
        self._load_products()

    def _update_cat_buttons(self):
        if not hasattr(self, "cat_frame"): return

        # Create buttons if they don't exist
        if not self.cat_buttons:
            cat_icons = {
                "Todos": "", "Abarrotes": "🌾", "Bebidas": "🥤", "Lácteos": "🥛",
                "Limpieza": "🧹", "Botanas": "🍿", "Panadería": "🥖",
                "Carnes frías": "🥩", "Higiene": "🧼", "Otros": "📦",
                "Quesos": "🧀", "Vinos": "🍷", "Dulces": "🍬", "Aceites": "🫒",
            }
            for cat in self._categories:
                icon  = cat_icons.get(cat, "")
                label = f"{icon} {cat}".upper() if icon else cat.upper()
                btn = tk.Label(self.cat_frame, text=label, font=ff(7, "bold"),
                               padx=16, pady=8, cursor="hand2", relief="flat")
                btn.pack(side="left", padx=(0, 8))
                btn.bind("<Button-1>", lambda e, c=cat: self._select_category(c))
                self.cat_buttons[cat] = btn

        for cat, btn in self.cat_buttons.items():
            if cat == self.active_category.get():
                btn.config(bg=C["on_primary"], fg=C["primary"])
            else:
                btn.config(bg=C["primary_container"], fg=C["on_primary_container"])

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
        raw_emoji = p.get("emoji", p.get("imagen_url", "📦"))
        emoji     = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"

        # Tonal Layering: Background lowest (white) on background low (cream)
        card = tk.Frame(
            self.prod_inner,
            bg=C["surface_lowest"],
            cursor="hand2" if not is_out else "arrow",
            highlightthickness=0
        )
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        inner = tk.Frame(card, bg=C["surface_lowest"], padx=16, pady=16)
        inner.pack(fill="both", expand=True)

        # Image placeholder frame
        img_placeholder = tk.Frame(inner, bg=C["surface_low"], height=160)
        img_placeholder.pack(fill="x", pady=(0, 12))
        img_placeholder.pack_propagate(False)
        tk.Label(img_placeholder, text=emoji, font=ff(40), bg=C["surface_low"]).place(relx=0.5, rely=0.5, anchor="center")

        # Category tag
        cat_text = p.get("categoria", "").upper()
        tk.Label(inner, text=cat_text, font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg=C["secondary"], anchor="w").pack(fill="x")

        # Headline
        name_lbl = tk.Label(inner, text=p["nombre"], font=fh(12, "bold"),
                            bg=C["surface_lowest"], fg=C["on_surface"] if not is_out else C["on_surface_variant"],
                            anchor="w", wraplength=160, justify="left")
        name_lbl.pack(fill="x", pady=(4, 8))

        # Bottom row: Price and Stock
        bottom = tk.Frame(inner, bg=C["surface_lowest"])
        bottom.pack(fill="x", side="bottom")

        price = float(p.get("precio_venta", p.get("precio_venta", 0)))
        price_lbl = tk.Label(bottom, text=f"${price:,.2f}",
                             font=ff(14, "bold"), bg=C["surface_lowest"],
                             fg=C["primary"] if not is_out else C["on_surface_variant"])
        price_lbl.pack(side="left")

        if is_out:
            badge = tk.Label(bottom, text="OUT OF STOCK", font=ff(6, "bold"),
                             bg=C["chip_red"], fg=C["red"], padx=6, pady=2)
            badge.pack(side="right")
        elif is_low:
            badge = tk.Label(bottom, text=f"ONLY {stock}", font=ff(6, "bold"),
                             bg=C["chip_amber"], fg=C["amber"], padx=6, pady=2)
            badge.pack(side="right")
        else:
            badge = tk.Label(bottom, text=f"{stock} IN STOCK", font=ff(6, "bold"),
                             bg=C["chip_green"], fg=C["primary"], padx=6, pady=2)
            badge.pack(side="right")

        def on_enter(e, c=card):
            if not is_out:
                c.config(bg=C["surface_high"])
                for w in c.winfo_children():
                    if isinstance(w, tk.Frame): w.config(bg=C["surface_high"])
                    for sw in w.winfo_children():
                        if isinstance(sw, (tk.Label, tk.Frame)): sw.config(bg=C["surface_high"])

        def on_leave(e, c=card):
            c.config(bg=C["surface_lowest"])
            for w in c.winfo_children():
                if isinstance(w, tk.Frame): w.config(bg=C["surface_lowest"])
                for sw in w.winfo_children():
                    if isinstance(sw, (tk.Label, tk.Frame)): sw.config(bg=C["surface_lowest"])
            # Reset image placeholder which has a different background
            img_placeholder.config(bg=C["surface_low"])
            for sw in img_placeholder.winfo_children(): sw.config(bg=C["surface_low"])

        def on_click(e, prod=p):
            if not is_out:
                self._add_to_cart(prod)

        for widget in [card, inner, img_placeholder, name_lbl, price_lbl, bottom]:
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
        t_header = tk.Frame(parent, bg=C["surface_lowest"], padx=24, pady=24)
        t_header.grid(row=0, column=0, sticky="ew")

        tk.Label(t_header, text="Current Ticket", font=fh(16, "bold"),
                 bg=C["surface_lowest"], fg=C["primary"]).pack(side="left")

        clear_btn = tk.Label(t_header, text="🗑", font=ff(12),
                             bg=C["surface_lowest"], fg=C["on_surface_variant"], padx=8, pady=4, cursor="hand2")
        clear_btn.pack(side="right")
        clear_btn.bind("<Button-1>", lambda e: self._clear_cart())

        self.lbl_items_count = tk.Label(t_header, text="",
                                         font=ff(7, "bold"),
                                         bg=C["surface_low"], fg=C["primary"],
                                         padx=8, pady=3)
        self.lbl_items_count.pack(side="right", padx=8)

        # Sub-header info
        sub_info = tk.Frame(parent, bg=C["surface_lowest"], padx=24)
        sub_info.grid(row=0, column=0, sticky="ew", pady=(64, 12))
        tk.Label(sub_info, text="👤 CUSTOMER: GUEST WALKER • TICKET #402",
                 font=ff(7, "bold"), bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(anchor="w")

        tk.Frame(parent, bg=C["surface_low"], height=1).grid(row=0, column=0, sticky="ews",
                                                         padx=24, pady=(0, 0))

        # Fila 1: Carrito scrollable
        cart_wrap = tk.Frame(parent, bg=C["surface_lowest"])
        cart_wrap.grid(row=1, column=0, sticky="nsew")

        self.cart_canvas = tk.Canvas(cart_wrap, bg=C["surface_lowest"], highlightthickness=0)
        cart_scroll = tk.Scrollbar(cart_wrap, orient="vertical",
                                   command=self.cart_canvas.yview)
        cart_scroll.pack(side="right", fill="y")
        self.cart_canvas.pack(side="left", fill="both", expand=True)
        self.cart_canvas.configure(yscrollcommand=cart_scroll.set)

        self.cart_inner = tk.Frame(self.cart_canvas, bg=C["surface_lowest"], padx=24)
        self._cart_window = self.cart_canvas.create_window((0, 0), window=self.cart_inner,
                                                            anchor="nw")
        self.cart_inner.bind("<Configure>", lambda e: self.cart_canvas.configure(
            scrollregion=self.cart_canvas.bbox("all")))
        self.cart_canvas.bind("<Configure>", lambda e: self.cart_canvas.itemconfig(
            self._cart_window, width=e.width))

        # Fila 2: Pie (totales + pago + cobrar)
        pie = tk.Frame(parent, bg=C["surface_high"])
        pie.grid(row=2, column=0, sticky="ew")

        totals_inner = tk.Frame(pie, bg=C["surface_high"], padx=24, pady=24)
        totals_inner.pack(fill="x")

        r_sub = tk.Frame(totals_inner, bg=C["surface_high"])
        r_sub.pack(fill="x", pady=1)
        tk.Label(r_sub, text="Subtotal", font=ff(8),
                 bg=C["surface_high"], fg=C["on_surface_variant"]).pack(side="left")
        self.lbl_subtotal = tk.Label(r_sub, text="$0.00", font=ff(8, "bold"),
                                      bg=C["surface_high"], fg=C["on_surface_variant"])
        self.lbl_subtotal.pack(side="right")

        r_tax = tk.Frame(totals_inner, bg=C["surface_high"])
        r_tax.pack(fill="x", pady=1)
        tk.Label(r_tax, text="Tax (16%)", font=ff(8),
                 bg=C["surface_high"], fg=C["on_surface_variant"]).pack(side="left")
        self.lbl_tax = tk.Label(r_tax, text="$0.00", font=ff(8, "bold"),
                                 bg=C["surface_high"], fg=C["on_surface_variant"])
        self.lbl_tax.pack(side="right")

        tk.Frame(totals_inner, bg=C["surface_highest"], height=1).pack(fill="x", pady=12)

        r_total = tk.Frame(totals_inner, bg=C["surface_high"])
        r_total.pack(fill="x", pady=(0, 16))
        tk.Label(r_total, text="Total", font=fh(18, "italic"),
                 bg=C["surface_high"], fg=C["primary"]).pack(side="left")
        self.lbl_total = tk.Label(r_total, text="$0.00", font=ff(24, "bold"),
                                   bg=C["surface_high"], fg=C["primary"])
        self.lbl_total.pack(side="right")

        # Método de pago
        pay_frame = tk.Frame(pie, bg=C["surface_high"], padx=24, pady=8)
        pay_frame.pack(fill="x")

        self.btn_efectivo = tk.Label(pay_frame, text="💵  EFECTIVO",
                                      font=ff(7, "bold"), padx=20, pady=16,
                                      bg=C["surface_lowest"], fg=C["on_surface"],
                                      cursor="hand2", relief="flat", highlightthickness=1,
                                      highlightbackground=C["outline_variant"])
        self.btn_efectivo.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_tarjeta = tk.Label(pay_frame, text="💳  TARJETA",
                                     font=ff(7, "bold"), padx=20, pady=16,
                                     bg=C["surface_lowest"], fg=C["on_surface"],
                                     cursor="hand2", relief="flat", highlightthickness=1,
                                     highlightbackground=C["outline_variant"])
        self.btn_tarjeta.pack(side="left", fill="x", expand=True, padx=(4, 0))

        self.btn_efectivo.bind("<Button-1>", lambda e: self._set_payment("efectivo"))
        self.btn_tarjeta.bind("<Button-1>",  lambda e: self._set_payment("tarjeta"))
        self._update_pay_btns()

        # Botón Cobrar
        btn_area = tk.Frame(pie, bg=C["surface_high"])
        btn_area.pack(fill="x", padx=24, pady=(4, 24))

        self.btn_cobrar_canvas = tk.Canvas(btn_area, bg=C["surface_high"],
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
        self.bind_all("<F1>", lambda e: self.hdr_search_entry.focus_set())
        self.bind_all("<F2>", lambda e: self._process_sale())
        self.bind_all("<F3>", lambda e: self._clear_cart())
        self.bind_all("<Escape>", lambda e: (self.search_var.set(""),
                                              self.hdr_search_entry.focus_set()))

    def _draw_cobrar_btn(self, amount_text, enabled=True):
        self._last_cobrar_text    = amount_text
        self._last_cobrar_enabled = enabled
        c = self.btn_cobrar_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 10:
            return
        h = 50
        r = 12
        fill = C["primary"] if enabled else C["surface_highest"]
        text_color = "white" if enabled else C["on_surface_variant"]

        # Rounded corners for the button
        c.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=fill, outline=fill)
        c.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=fill, outline=fill)
        c.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=fill, outline=fill)
        c.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=fill, outline=fill)
        c.create_rectangle(r, 0, w-r, h, fill=fill, outline=fill)
        c.create_rectangle(0, r, w, h-r, fill=fill, outline=fill)

        text = f"COMPLETE TRANSACTION →" if enabled else "SELECT ITEMS"
        c.create_text(w//2, h//2, text=text, fill=text_color,
                      font=ff(9, "bold"), anchor="center")
        c.config(cursor="hand2" if enabled else "arrow")

    def _set_payment(self, method):
        self.pay_var.set(method)
        self._update_pay_btns()

    def _update_pay_btns(self):
        sel = self.pay_var.get()
        if sel == "efectivo":
            self.btn_efectivo.config(bg=C["primary"], fg="white", highlightbackground=C["primary"])
            self.btn_tarjeta.config(bg=C["surface_lowest"], fg=C["on_surface"], highlightbackground=C["outline_variant"])
        else:
            self.btn_tarjeta.config(bg=C["primary"], fg="white", highlightbackground=C["primary"])
            self.btn_efectivo.config(bg=C["surface_lowest"], fg=C["on_surface"], highlightbackground=C["outline_variant"])

    # ────────────────────────────────────────────────────────────
    #  RENDER CART
    # ────────────────────────────────────────────────────────────
    def _render_cart(self):
        for w in self.cart_inner.winfo_children():
            w.destroy()

        if not self.cart:
            empty_frame = tk.Frame(self.cart_inner, bg=C["surface_lowest"])
            empty_frame.pack(fill="both", expand=True, padx=20, pady=60)
            tk.Label(empty_frame, text="🛒", font=ff(36),
                     bg=C["surface_lowest"], fg=C["surface_highest"]).pack()
            tk.Label(empty_frame, text="Ticket vacío", font=fh(12, "bold"),
                     bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(pady=(8, 4))
            tk.Label(empty_frame, text="Escanea un código o agrega productos",
                     font=ff(9), bg=C["surface_lowest"], fg=C["on_surface_variant"],
                     wraplength=200, justify="center").pack()
            return

        for i, item in enumerate(self.cart):
            p = item["product"]
            item_frame = tk.Frame(self.cart_inner, bg=C["surface_lowest"], pady=12)
            item_frame.pack(fill="x")

            r1 = tk.Frame(item_frame, bg=C["surface_lowest"])
            r1.pack(fill="x")

            raw_emoji = p.get("emoji", p.get("imagen_url", "📦"))
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"

            # Small image box
            img_box = tk.Frame(r1, bg=C["surface_low"], width=48, height=48)
            img_box.pack(side="left", padx=(0, 12))
            img_box.pack_propagate(False)
            tk.Label(img_box, text=emoji, font=ff(16), bg=C["surface_low"]).place(relx=0.5, rely=0.5, anchor="center")

            info = tk.Frame(r1, bg=C["surface_lowest"])
            info.pack(side="left", fill="x", expand=True)

            nombre = p.get("nombre", "")
            tk.Label(info, text=nombre, font=ff(9, "bold"),
                     bg=C["surface_lowest"], fg=C["on_surface"], anchor="w").pack(fill="x")

            tk.Label(info, text=f"QTY: {item['qty']}", font=ff(7),
                     bg=C["surface_lowest"], fg=C["on_surface_variant"], anchor="w").pack(fill="x")

            price_val = float(item['subtotal'])
            tk.Label(r1, text=f"${price_val:,.2f}",
                     font=ff(10, "bold"), bg=C["surface_lowest"], fg=C["primary"]).pack(side="right")

            r2 = tk.Frame(item_frame, bg=C["surface_lowest"])
            r2.pack(fill="x", pady=(4, 0))

            del_btn = tk.Label(r2, text="REMOVE", font=ff(6, "bold"),
                               bg=C["surface_lowest"], fg=C["error"], cursor="hand2")
            del_btn.pack(side="left")
            del_btn.bind("<Button-1>", lambda e, idx=i: self._remove_item(idx))

            # Qty controls
            ctrl = tk.Frame(r2, bg=C["surface_low"])
            ctrl.pack(side="right")

            minus = tk.Label(ctrl, text=" − ", font=ff(9, "bold"),
                             bg=C["surface_low"], fg=C["on_surface"], cursor="hand2", pady=2)
            minus.pack(side="left")
            minus.bind("<Button-1>", lambda e, idx=i: self._change_qty(idx, -1))

            tk.Label(ctrl, text=f" {item['qty']} ", font=ff(8, "bold"),
                     bg=C["surface_low"], fg=C["on_surface"]).pack(side="left")

            plus = tk.Label(ctrl, text=" + ", font=ff(9, "bold"),
                            bg=C["surface_low"], fg=C["primary"], cursor="hand2", pady=2)
            plus.pack(side="left")
            plus.bind("<Button-1>", lambda e, idx=i: self._change_qty(idx, 1))
            # In editorial style, we might want to keep it simple.

            if i < len(self.cart) - 1:
                # Dotted/Dashed separator effect
                sep = tk.Frame(self.cart_inner, bg=C["outline_variant"], height=1)
                sep.pack(fill="x", pady=4)
                # Note: Tkinter doesn't have easy dashed lines for frames,
                # so we use a very thin line or tonal shift.

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
        self.hdr_search_entry.focus_set()

    # ════════════════════════════════════════════════════════════
    #  MODAL EFECTIVO
    # ════════════════════════════════════════════════════════════
    def _show_cash_modal(self, folio, total, subtotal, tax, cart_snapshot):
        dlg = tk.Toplevel(self)
        dlg.title("CASH PAYMENT")
        dlg.configure(bg=C["surface_lowest"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 460, 680
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg=C["primary"], pady=32)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💵", font=ff(32), bg=C["primary"]).pack()
        tk.Label(hdr, text="CASH PAYMENT", font=fh(16, "bold"),
                 bg=C["primary"], fg="white").pack(pady=(4, 0))
        tk.Label(hdr, text=f"TICKET {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}".upper(),
                 font=ff(7, "bold"), bg=C["primary"], fg=C["on_primary_container"]).pack()

        body = tk.Frame(dlg, bg=C["surface_lowest"])
        body.pack(fill="both", expand=True, padx=32, pady=24)

        items_bg = tk.Frame(body, bg=C["surface_low"], pady=8)
        items_bg.pack(fill="x", pady=(0, 16))
        for item in cart_snapshot:
            r = tk.Frame(items_bg, bg=C["surface_low"])
            r.pack(fill="x", padx=16, pady=2)
            nombre = item["product"].get("nombre", "")
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(8), bg=C["surface_low"],
                     fg=C["on_surface"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=ff(8, "bold"),
                     bg=C["surface_low"], fg=C["on_surface"]).pack(side="right")

        t_row = tk.Frame(body, bg=C["surface_lowest"])
        t_row.pack(fill="x")
        for lbl, val in [("SUBTOTAL", f"${subtotal:,.2f}"), ("TAX 16%", f"${tax:,.2f}")]:
            r = tk.Frame(t_row, bg=C["surface_lowest"])
            r.pack(fill="x", pady=1)
            tk.Label(r, text=lbl, font=ff(7, "bold"), bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(side="left")
            tk.Label(r, text=val, font=ff(8, "bold"), bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(side="right")

        tk.Frame(body, bg=C["surface_high"], height=1).pack(fill="x", pady=12)

        r_t = tk.Frame(body, bg=C["surface_lowest"])
        r_t.pack(fill="x")
        tk.Label(r_t, text="TOTAL", font=fh(14, "bold italic"),
                 bg=C["surface_lowest"], fg=C["primary"]).pack(side="left")
        tk.Label(r_t, text=f"${total:,.2f}", font=ff(20, "bold"),
                 bg=C["surface_lowest"], fg=C["primary"]).pack(side="right")

        tk.Frame(body, bg=C["surface_high"], height=1).pack(fill="x", pady=16)

        tk.Label(body, text="CUSTOMER PAID WITH:", font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(anchor="w")

        cash_wrap = tk.Frame(body, bg=C["surface_highest"],
                             highlightthickness=0)
        cash_wrap.pack(fill="x", pady=(4, 0))
        tk.Label(cash_wrap, text="$", font=ff(14, "bold"),
                 bg=C["surface_highest"], fg=C["on_surface"], padx=16).pack(side="left")
        cash_var = tk.StringVar()
        entry_cash = tk.Entry(cash_wrap, textvariable=cash_var,
                              font=ff(16, "bold"), bg=C["surface_highest"],
                              fg=C["on_surface"], insertbackground=C["primary"],
                              relief="flat", bd=0, width=12, justify="right")
        entry_cash.pack(side="left", fill="x", expand=True, pady=16, padx=(0, 16))
        entry_cash.focus_set()

        change_frame = tk.Frame(body, bg=C["surface_lowest"])
        change_frame.pack(fill="x", pady=12)
        tk.Label(change_frame, text="CHANGE DUE:", font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(side="left")
        lbl_change = tk.Label(change_frame, text="—", font=ff(18, "bold"),
                              bg=C["surface_lowest"], fg=C["on_surface"])
        lbl_change.pack(side="right")

        quick_frame = tk.Frame(body, bg=C["surface_lowest"])
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
            b = tk.Label(quick_frame, text=f"${int(amt):,}", font=ff(7, "bold"),
                         bg=C["surface_low"], fg=C["on_surface"], padx=12, pady=8,
                         cursor="hand2", relief="flat")
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, a=amt: set_amount(a))

        def _recalc(*args):
            try:
                paid_str = cash_var.get().replace(",", "")
                if not paid_str:
                    lbl_change.config(text="—", fg=C["on_surface"])
                    btn_confirm.config(state="disabled", bg=C["surface_high"], fg=C["on_surface_variant"])
                    return
                paid = float(paid_str)
                cambio = paid - total
                if cambio < 0:
                    lbl_change.config(text=f"-${abs(cambio):,.2f}", fg=C["error"])
                    btn_confirm.config(state="disabled", bg=C["surface_high"], fg=C["on_surface_variant"])
                else:
                    lbl_change.config(text=f"${cambio:,.2f}", fg=C["primary"])
                    btn_confirm.config(state="normal", bg=C["primary"], fg="white")
            except ValueError:
                lbl_change.config(text="—", fg=C["on_surface"])
                btn_confirm.config(state="disabled", bg=C["surface_high"], fg=C["on_surface_variant"])

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

        btn_confirm = tk.Button(body, text="COMPLETE CASH SALE",
                                font=ff(9, "bold"),
                                bg=C["surface_high"], fg=C["on_surface_variant"],
                                activebackground=C["primary"],
                                relief="flat", bd=0, cursor="hand2",
                                state="disabled",
                                command=_confirm_cash)
        btn_confirm.pack(fill="x", ipady=16, pady=(12, 4))

        btn_cancel = tk.Button(body, text="CANCEL TRANSACTION",
                               font=ff(7, "bold"), bg=C["surface_lowest"], fg=C["on_surface_variant"],
                               activebackground=C["surface_low"],
                               relief="flat", bd=0, cursor="hand2",
                               command=lambda: [dlg.destroy(), self._reset_for_new_sale()])
        btn_cancel.pack(fill="x", ipady=8)

        dlg.bind("<Escape>", lambda e: [dlg.destroy(), self._reset_for_new_sale()])

    # ════════════════════════════════════════════════════════════
    #  MODAL ÉXITO EFECTIVO
    # ════════════════════════════════════════════════════════════
    def _show_cash_success(self, folio, total, subtotal, tax,
                           cart_snapshot, paid, cambio):
        dlg = tk.Toplevel(self)
        dlg.title("TRANSACTION COMPLETE")
        dlg.configure(bg=C["surface_lowest"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 420, 560
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg=C["surface_lowest"])
        hdr.pack(fill="x", padx=32, pady=24)
        tk.Label(hdr, text="SUCCESS", font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg=C["primary"]).pack(side="left")

        chk_bg = tk.Frame(dlg, bg=C["green_pale"], width=64, height=64)
        chk_bg.pack(pady=8)
        chk_bg.pack_propagate(False)
        tk.Label(chk_bg, text="✓", font=ff(24, "bold"),
                 bg=C["green_pale"], fg=C["primary"]).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(dlg, text="Venta Exitosa", font=fh(18, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface"]).pack(pady=(8, 2))
        tk.Label(dlg,
                 text=f"TICKET {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}".upper(),
                 font=ff(7, "bold"), bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack()

        cambio_frame = tk.Frame(dlg, bg=C["surface_low"], pady=16)
        cambio_frame.pack(fill="x", padx=32, pady=20)
        tk.Label(cambio_frame, text="CHANGE DUE", font=ff(7, "bold"),
                 bg=C["surface_low"], fg=C["on_surface_variant"]).pack()
        tk.Label(cambio_frame, text=f"${cambio:,.2f}", font=ff(24, "bold"),
                 bg=C["surface_low"], fg=C["primary"]).pack()
        tk.Label(cambio_frame,
                 text=f"Received: ${paid:,.2f}  ·  Total: ${total:,.2f}",
                 font=ff(7), bg=C["surface_low"], fg=C["on_surface_variant"]).pack(pady=(4, 0))

        items_bg = tk.Frame(dlg, bg=C["surface_lowest"])
        items_bg.pack(fill="x", padx=32, pady=(0, 12))
        items_inner = tk.Frame(items_bg, bg=C["surface_low"], padx=16, pady=12)
        items_inner.pack(fill="x")
        for item in cart_snapshot:
            r = tk.Frame(items_inner, bg=C["surface_low"])
            r.pack(fill="x", pady=2)
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            nombre = item["product"].get("nombre", "")
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(8), bg=C["surface_low"],
                     fg=C["on_surface"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=ff(8, "bold"),
                     bg=C["surface_low"], fg=C["on_surface"]).pack(side="right")

        btn_row = tk.Frame(dlg, bg=C["surface_lowest"])
        btn_row.pack(fill="x", padx=32, pady=(0, 12))
        tk.Button(btn_row, text="PRINT RECEIPT", font=ff(7, "bold"),
                  bg=C["surface_high"], fg=C["on_surface"], relief="flat", bd=0,
                  padx=12, pady=10, cursor="hand2").pack(side="left", fill="x",
                                                         expand=True, padx=(0, 8))
        tk.Button(btn_row, text="SEND EMAIL", font=ff(7, "bold"),
                  bg=C["surface_high"], fg=C["on_surface"], relief="flat", bd=0,
                  padx=12, pady=10, cursor="hand2").pack(side="left", fill="x", expand=True)

        def close_and_reset():
            dlg.destroy()
            self._reset_for_new_sale()

        nueva_btn = tk.Button(dlg, text="NEW TRANSACTION",
                              font=ff(9, "bold"),
                              bg=C["primary"], fg="white",
                              activebackground=C["primary"],
                              relief="flat", bd=0, cursor="hand2",
                              command=close_and_reset)
        nueva_btn.pack(fill="x", padx=32, pady=(4, 24), ipady=16)
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
        dlg.title("CARD PAYMENT")
        dlg.configure(bg=C["surface_lowest"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 440, 580
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg="#1A2B4A", pady=32)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💳", font=ff(32), bg="#1A2B4A").pack()
        tk.Label(hdr, text="CARD PAYMENT", font=fh(16, "bold"),
                 bg="#1A2B4A", fg="white").pack(pady=(4, 0))
        tk.Label(hdr,
                 text=f"TICKET {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}".upper(),
                 font=ff(7, "bold"), bg="#1A2B4A", fg="#7A9CC0").pack()

        body = tk.Frame(dlg, bg=C["surface_lowest"])
        body.pack(fill="both", expand=True, padx=32, pady=24)

        total_frame = tk.Frame(body, bg=C["surface_lowest"])
        total_frame.pack(pady=(0, 16))
        tk.Label(total_frame, text="TOTAL TO CHARGE", font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack()
        tk.Label(total_frame, text=f"${total:,.2f}", font=ff(24, "bold"),
                 bg=C["surface_lowest"], fg="#1A2B4A").pack()

        terminal_frame = tk.Frame(body, bg="#F0F4FA", pady=20)
        terminal_frame.pack(fill="x", pady=(0, 16))
        tk.Label(terminal_frame, text="⬛", font=ff(28),
                 bg="#F0F4FA", fg="#333").pack()
        tk.Label(terminal_frame, text="Pointer  ·  Terminal not connected",
                 font=ff(8, "bold"), bg="#F0F4FA", fg="#1A2B4A").pack(pady=(6, 2))
        lbl_status = tk.Label(terminal_frame,
                               text="⚠  Integración pendiente — confirma manualmente",
                               font=ff(8), bg="#F0F4FA", fg=C["amber"])
        lbl_status.pack()

        prog_outer = tk.Frame(body, bg=C["surface_high"], height=4)
        prog_outer.pack(fill="x", pady=4)
        prog_bar = tk.Frame(prog_outer, bg="#1A2B4A", height=4, width=0)
        prog_bar.place(x=0, y=0, relheight=1)

        items_bg = tk.Frame(body, bg=C["surface_low"], pady=8)
        items_bg.pack(fill="x", pady=(8, 0))
        for item in cart_snapshot:
            r = tk.Frame(items_bg, bg=C["surface_low"])
            r.pack(fill="x", padx=16, pady=2)
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            nombre = item["product"].get("nombre", "")
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(8), bg=C["surface_low"],
                     fg=C["on_surface"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=ff(8, "bold"),
                     bg=C["surface_low"], fg=C["on_surface"]).pack(side="right")

        def _confirm_card():
            dlg.destroy()
            self._show_card_success(folio, total, subtotal, tax, cart_snapshot)

        btn_confirm = tk.Button(body, text="CONFIRM MANUAL PAYMENT",
                                font=ff(9, "bold"),
                                bg="#1A2B4A", fg="white",
                                activebackground="#243D6A",
                                relief="flat", bd=0, cursor="hand2",
                                command=_confirm_card)
        btn_confirm.pack(fill="x", ipady=16, pady=(16, 4))

        btn_cancel = tk.Button(body, text="CANCEL TRANSACTION",
                               font=ff(7, "bold"), bg=C["surface_lowest"], fg=C["on_surface_variant"],
                               activebackground=C["surface_low"],
                               relief="flat", bd=0, cursor="hand2",
                               command=lambda: [dlg.destroy(), self._reset_for_new_sale()])
        btn_cancel.pack(fill="x", ipady=8)

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
        dlg.title("TRANSACTION COMPLETE")
        dlg.configure(bg=C["surface_lowest"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)

        w, h = 420, 560
        x = self.winfo_x() + (self.winfo_width()  - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(dlg, bg=C["surface_lowest"])
        hdr.pack(fill="x", padx=32, pady=24)
        tk.Label(hdr, text="SUCCESS", font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg="#1A2B4A").pack(side="left")

        chk_bg = tk.Frame(dlg, bg="#EEF2FF", width=64, height=64)
        chk_bg.pack(pady=8)
        chk_bg.pack_propagate(False)
        tk.Label(chk_bg, text="✓", font=ff(24, "bold"),
                 bg="#EEF2FF", fg="#1A2B4A").place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(dlg, text="Pago Aprobado", font=fh(18, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface"]).pack(pady=(8, 2))
        tk.Label(dlg,
                 text=f"TICKET {folio}  ·  {datetime.now().strftime('%d %b %Y  %I:%M %p')}".upper(),
                 font=ff(7, "bold"), bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack()

        total_f = tk.Frame(dlg, bg="#EEF2FF", pady=16)
        total_f.pack(fill="x", padx=32, pady=20)
        tk.Label(total_f, text=f"${total:,.2f}", font=ff(24, "bold"),
                 bg="#EEF2FF", fg="#1A2B4A").pack()
        tk.Label(total_f, text="CARD PAYMENT", font=ff(7, "bold"),
                 bg="#EEF2FF", fg="#4A6A9A").pack()

        items_bg = tk.Frame(dlg, bg=C["surface_lowest"])
        items_bg.pack(fill="x", padx=32, pady=(0, 12))
        items_inner = tk.Frame(items_bg, bg=C["surface_low"], padx=16, pady=12)
        items_inner.pack(fill="x")
        for item in cart_snapshot:
            r = tk.Frame(items_inner, bg=C["surface_low"])
            r.pack(fill="x", pady=2)
            raw_emoji = item["product"].get("emoji", "📦")
            emoji = raw_emoji if len(str(raw_emoji)) <= 4 else "📦"
            nombre = item["product"].get("nombre", "")
            name = f"{emoji} {nombre} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(8), bg=C["surface_low"],
                     fg=C["on_surface"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=ff(8, "bold"),
                     bg=C["surface_low"], fg=C["on_surface"]).pack(side="right")

        btn_row = tk.Frame(dlg, bg=C["surface_lowest"])
        btn_row.pack(fill="x", padx=32, pady=(0, 12))
        tk.Button(btn_row, text="PRINT RECEIPT", font=ff(7, "bold"),
                  bg=C["surface_high"], fg=C["on_surface"], relief="flat", bd=0,
                  padx=12, pady=10, cursor="hand2").pack(side="left", fill="x",
                                                         expand=True, padx=(0, 8))
        tk.Button(btn_row, text="SEND EMAIL", font=ff(7, "bold"),
                  bg=C["surface_high"], fg=C["on_surface"], relief="flat", bd=0,
                  padx=12, pady=10, cursor="hand2").pack(side="left", fill="x", expand=True)

        def close_and_reset():
            dlg.destroy()
            self._reset_for_new_sale()

        nueva_btn = tk.Button(dlg, text="NEW TRANSACTION",
                              font=ff(9, "bold"),
                              bg="#1A2B4A", fg="white",
                              activebackground="#243D6A",
                              relief="flat", bd=0, cursor="hand2",
                              command=close_and_reset)
        nueva_btn.pack(fill="x", padx=32, pady=(4, 24), ipady=16)
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

        card = tk.Frame(self, bg=C["surface_lowest"], padx=36, pady=32)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Iniciar sesión", font=fh(15, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface"]).pack(anchor="w")
        tk.Label(card, text="Ingresa tus credenciales para continuar",
                 font=ff(9), bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(anchor="w", pady=(2, 20))

        tk.Label(card, text="USUARIO", font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(anchor="w")
        user_wrap = tk.Frame(card, bg=C["surface_highest"],
                             highlightthickness=0)
        user_wrap.pack(fill="x", pady=(4, 14))
        self.entry_user = tk.Entry(user_wrap, font=ff(11), bg=C["surface_highest"], fg=C["on_surface"],
                                   insertbackground=C["primary"], relief="flat", bd=0)
        self.entry_user.pack(fill="x", padx=12, pady=12)
        self.entry_user.bind("<FocusIn>",
                             lambda e: user_wrap.config(bg=C["surface_high"]))
        self.entry_user.bind("<FocusOut>",
                             lambda e: user_wrap.config(bg=C["surface_highest"]))
        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus_set())

        tk.Label(card, text="CONTRASEÑA", font=ff(7, "bold"),
                 bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(anchor="w")
        pass_wrap = tk.Frame(card, bg=C["surface_highest"],
                             highlightthickness=0)
        pass_wrap.pack(fill="x", pady=(4, 6))
        self.entry_pass = tk.Entry(pass_wrap, font=ff(11), bg=C["surface_highest"], fg=C["on_surface"],
                                   insertbackground=C["primary"], show="●", relief="flat", bd=0)
        self.entry_pass.pack(fill="x", padx=12, pady=12)
        self.entry_pass.bind("<FocusIn>",
                             lambda e: pass_wrap.config(bg=C["surface_high"]))
        self.entry_pass.bind("<FocusOut>",
                             lambda e: pass_wrap.config(bg=C["surface_highest"]))
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = tk.Label(card, text="", font=ff(9),
                                   bg=C["surface_lowest"], fg=C["error"])
        self.lbl_error.pack(anchor="w", pady=(0, 12))

        login_btn = tk.Button(card, text="ENTRAR", font=ff(9, "bold"),
                              bg=C["primary"], fg="white",
                              activebackground=C["primary"],
                              relief="flat", bd=0, cursor="hand2",
                              command=self._do_login)
        login_btn.pack(fill="x", ipady=14)

        tk.Label(card, text="usuario: prueba  ·  contraseña: prueba",
                 font=ff(7), bg=C["surface_lowest"], fg=C["on_surface_variant"]).pack(pady=(14, 0))

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