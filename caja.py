"""
La Casita Delicatessen — Sistema de Caja
Rediseño moderno con conexión a Neon PostgreSQL
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
    {"id": 1, "sku": "QSO-001", "name": "Queso Manchego",       "price": 189.00, "stock": 24, "category": "Quesos",      "unit": "kg",    "emoji": "🧀"},
    {"id": 2, "sku": "CRN-002", "name": "Jamón Serrano",         "price": 320.00, "stock": 5,  "category": "Carnes Frías", "unit": "kg",    "emoji": "🥩"},
    {"id": 3, "sku": "VIN-003", "name": "Vino Tinto Reserva",    "price": 285.00, "stock": 12, "category": "Vinos",       "unit": "pza",   "emoji": "🍷"},
    {"id": 4, "sku": "PAN-004", "name": "Pan Baguette",           "price": 45.00,  "stock": 20, "category": "Panadería",   "unit": "pza",   "emoji": "🥖"},
    {"id": 5, "sku": "ACE-005", "name": "Aceite de Oliva Extra",  "price": 198.00, "stock": 9,  "category": "Aceites",     "unit": "500ml", "emoji": "🫒"},
    {"id": 6, "sku": "DLC-006", "name": "Chocolate Belga",        "price": 125.00, "stock": 3,  "category": "Dulces",      "unit": "pza",   "emoji": "🍫"},
    {"id": 7, "sku": "QSO-007", "name": "Queso Brie",             "price": 165.00, "stock": 7,  "category": "Quesos",      "unit": "pza",   "emoji": "🧀"},
    {"id": 8, "sku": "CRN-008", "name": "Salami Italiano",        "price": 145.00, "stock": 0,  "category": "Carnes Frías", "unit": "kg",   "emoji": "🥩"},
    {"id": 9, "sku": "VIN-009", "name": "Prosecco Brut",          "price": 310.00, "stock": 15, "category": "Vinos",       "unit": "pza",   "emoji": "🥂"},
    {"id":10, "sku": "PAN-010", "name": "Croissant Mantequilla",  "price": 38.00,  "stock": 18, "category": "Panadería",   "unit": "pza",   "emoji": "🥐"},
    {"id":11, "sku": "DLC-011", "name": "Mermelada Artesanal",    "price": 89.00,  "stock": 2,  "category": "Dulces",      "unit": "pza",   "emoji": "🍓"},
    {"id":12, "sku": "QSO-011", "name": "Queso Gouda",            "price": 175.00, "stock": 11, "category": "Quesos",      "unit": "kg",    "emoji": "🧀"},
    {"id":13, "sku": "CRN-012", "name": "Paté de Campaña",        "price": 110.00, "stock": 6,  "category": "Carnes Frías", "unit": "pza",  "emoji": "🍖"},
    {"id":14, "sku": "ACE-014", "name": "Vinagre Balsámico",      "price": 155.00, "stock": 8,  "category": "Aceites",     "unit": "250ml", "emoji": "🫙"},
    {"id":15, "sku": "PAN-015", "name": "Pan de Nuez",            "price": 62.00,  "stock": 14, "category": "Panadería",   "unit": "pza",   "emoji": "🍞"},
    {"id":16, "sku": "DLC-016", "name": "Turrón de Almendra",     "price": 95.00,  "stock": 6,  "category": "Dulces",      "unit": "pza",   "emoji": "🍬"},
]

MOCK_USER     = {"id": "U01", "name": "María G.",  "role": "cajero"}
MOCK_LOCATION = {"id": "L01", "name": "Sucursal Centro"}

FOLIO_COUNTER = [4763]

CATEGORIES = ["Todos", "Quesos", "Carnes Frías", "Vinos", "Panadería", "Dulces", "Aceites"]


# ════════════════════════════════════════════════════════════════
#  DATABASE MANAGER
# ════════════════════════════════════════════════════════════════
class DBManager:
    def __init__(self):
        self.conn = None
        self.connected = False
        self._connect()

    def _connect(self):
        if not DB_AVAILABLE:
            return
        try:
            self.conn = psycopg2.connect(DB_URL, connect_timeout=5)
            self.conn.autocommit = False
            self.connected = True
            self._ensure_schema()
        except Exception as e:
            print(f"[DB] No se pudo conectar: {e}")
            self.connected = False

    def _ensure_schema(self):
        """Crea tablas si no existen."""
        try:
            cur = self.conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id          SERIAL PRIMARY KEY,
                    sku         VARCHAR(20) UNIQUE NOT NULL,
                    name        VARCHAR(200) NOT NULL,
                    price       NUMERIC(10,2) NOT NULL DEFAULT 0,
                    stock       INTEGER NOT NULL DEFAULT 0,
                    category    VARCHAR(100),
                    unit        VARCHAR(20) DEFAULT 'pza',
                    emoji       VARCHAR(10) DEFAULT '📦',
                    active      BOOLEAN DEFAULT TRUE,
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS sales (
                    id          SERIAL PRIMARY KEY,
                    folio       VARCHAR(20),
                    total       NUMERIC(10,2),
                    subtotal    NUMERIC(10,2),
                    tax         NUMERIC(10,2),
                    payment     VARCHAR(20),
                    cashier     VARCHAR(100),
                    location    VARCHAR(100),
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );
                CREATE TABLE IF NOT EXISTS sale_items (
                    id          SERIAL PRIMARY KEY,
                    sale_id     INTEGER REFERENCES sales(id),
                    product_id  INTEGER REFERENCES products(id),
                    product_name VARCHAR(200),
                    qty         INTEGER,
                    unit_price  NUMERIC(10,2),
                    subtotal    NUMERIC(10,2)
                );
            """)
            self.conn.commit()

            # Seed products si la tabla está vacía
            cur.execute("SELECT COUNT(*) FROM products")
            count = cur.fetchone()[0]
            if count == 0:
                for p in MOCK_PRODUCTS:
                    cur.execute("""
                        INSERT INTO products (sku, name, price, stock, category, unit, emoji)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (sku) DO NOTHING
                    """, (p["sku"], p["name"], p["price"], p["stock"],
                          p["category"], p["unit"], p["emoji"]))
                self.conn.commit()
        except Exception as e:
            print(f"[DB] Schema error: {e}")
            try: self.conn.rollback()
            except: pass

    def get_products(self, search="", category="Todos"):
        if not self.connected:
            return self._filter_mock(search, category)
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            q = "SELECT * FROM products WHERE active=TRUE"
            params = []
            if search:
                q += " AND (LOWER(name) LIKE %s OR LOWER(sku) LIKE %s)"
                params += [f"%{search.lower()}%", f"%{search.lower()}%"]
            if category and category != "Todos":
                q += " AND category=%s"
                params.append(category)
            q += " ORDER BY category, name"
            cur.execute(q, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            print(f"[DB] get_products error: {e}")
            return self._filter_mock(search, category)

    def _filter_mock(self, search, category):
        result = MOCK_PRODUCTS
        if search:
            result = [p for p in result if search.lower() in p["name"].lower()
                      or search.lower() in p["sku"].lower()]
        if category and category != "Todos":
            result = [p for p in result if p["category"] == category]
        return result

    def update_stock(self, product_id, delta):
        """delta negativo = descontar. Devuelve True si ok."""
        if not self.connected:
            # Mock: actualizar en lista local
            for p in MOCK_PRODUCTS:
                if p["id"] == product_id:
                    p["stock"] = max(0, p["stock"] + delta)
            return True
        try:
            cur = self.conn.cursor()
            cur.execute("""
                UPDATE products
                SET stock = GREATEST(0, stock + %s)
                WHERE id = %s
                RETURNING stock
            """, (delta, product_id))
            result = cur.fetchone()
            self.conn.commit()
            return result is not None
        except Exception as e:
            print(f"[DB] update_stock error: {e}")
            try: self.conn.rollback()
            except: pass
            return False

    def get_stock(self, product_id):
        """Obtiene el stock actual de la BD."""
        if not self.connected:
            p = next((x for x in MOCK_PRODUCTS if x["id"] == product_id), None)
            return p["stock"] if p else 0
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT stock FROM products WHERE id=%s", (product_id,))
            row = cur.fetchone()
            return row[0] if row else 0
        except:
            return 0

    def save_sale(self, folio, cart, total, subtotal, tax, payment, cashier, location):
        if not self.connected:
            return True
        try:
            cur = self.conn.cursor()
            cur.execute("""
                INSERT INTO sales (folio, total, subtotal, tax, payment, cashier, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (folio, total, subtotal, tax, payment, cashier, location))
            sale_id = cur.fetchone()[0]

            for item in cart:
                cur.execute("""
                    INSERT INTO sale_items (sale_id, product_id, product_name, qty, unit_price, subtotal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (sale_id, item["product"]["id"], item["product"]["name"],
                      item["qty"], item["product"]["price"], item["subtotal"]))

            self.conn.commit()
            return True
        except Exception as e:
            print(f"[DB] save_sale error: {e}")
            try: self.conn.rollback()
            except: pass
            return False

    def get_today_sales(self):
        if not self.connected:
            return []
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT * FROM sales
                WHERE created_at::date = CURRENT_DATE
                ORDER BY created_at DESC LIMIT 50
            """)
            return [dict(r) for r in cur.fetchall()]
        except:
            return []

    def close(self):
        if self.conn:
            try: self.conn.close()
            except: pass


# ════════════════════════════════════════════════════════════════
#  WIDGETS CUSTOM
# ════════════════════════════════════════════════════════════════
class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, width=120, height=38,
                 bg=None, fg=None, hover_bg=None, font_spec=None,
                 radius=8, **kwargs):
        bg = bg or C["green"]
        fg = fg or "#FFFFFF"
        hover_bg = hover_bg or C["green_hover"]
        font_spec = font_spec or ff(10, "bold")

        super().__init__(parent, width=width, height=height,
                         bg=parent.cget("bg"), highlightthickness=0, **kwargs)

        self._bg = bg
        self._hover_bg = hover_bg
        self._fg = fg
        self._text = text
        self._command = command
        self._radius = radius
        self._font = font_spec
        self._w = width
        self._h = height
        self._hovered = False

        self._draw(bg)
        self.bind("<Enter>", lambda e: self._on_enter())
        self.bind("<Leave>", lambda e: self._on_leave())
        self.bind("<Button-1>", lambda e: self._on_click())
        self.bind("<ButtonRelease-1>", lambda e: self._on_release())

    def _draw(self, fill):
        self.delete("all")
        r = self._radius
        w, h = self._w, self._h
        self.create_arc(0, 0, r*2, r*2, start=90, extent=90, fill=fill, outline=fill)
        self.create_arc(w-r*2, 0, w, r*2, start=0, extent=90, fill=fill, outline=fill)
        self.create_arc(0, h-r*2, r*2, h, start=180, extent=90, fill=fill, outline=fill)
        self.create_arc(w-r*2, h-r*2, w, h, start=270, extent=90, fill=fill, outline=fill)
        self.create_rectangle(r, 0, w-r, h, fill=fill, outline=fill)
        self.create_rectangle(0, r, w, h-r, fill=fill, outline=fill)
        self.create_text(w//2, h//2, text=self._text, fill=self._fg,
                         font=self._font, anchor="center")

    def _on_enter(self):
        self._draw(self._hover_bg)
        self.config(cursor="hand2")

    def _on_leave(self):
        self._draw(self._bg)

    def _on_click(self):
        self._draw(C["green"])

    def _on_release(self):
        self._draw(self._hover_bg if self._hovered else self._bg)
        if self._command:
            self._command()

    def update_text(self, text):
        self._text = text
        self._draw(self._bg)

    def set_state(self, enabled, bg=None):
        if bg:
            self._bg = bg
        self._draw(self._bg if enabled else C["text3"])


class Toast(tk.Toplevel):
    """Notificación flotante tipo toast."""
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

        # Centrar en pantalla
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + master.winfo_height() - 80
        self.geometry(f"+{x}+{y}")

        # Fade in / out
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
        self._db_status = "🟢 Conectado a Neon" if self.db.connected else "🟡 Modo offline (mock)"

        self._build_ui()
        self._load_products()
        self._start_clock()

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

        # Izquierda: logo + sucursal
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

        # Centro: estado de caja
        center = tk.Frame(hdr, bg=C["header"])
        center.place(relx=0.5, rely=0.5, anchor="center")

        caja_badge = tk.Frame(center, bg=C["header2"], padx=12, pady=4)
        caja_badge.pack(side="left", padx=8)
        self.lbl_session_dot = tk.Label(caja_badge, text="●", font=ff(8),
                                         bg=C["header2"], fg=C["green_light"])
        self.lbl_session_dot.pack(side="left", padx=(0,4))
        tk.Label(caja_badge, text="Caja abierta · Turno 1", font=ff(9),
                 bg=C["header2"], fg=C["header_text"]).pack(side="left")

        tk.Label(center, text="Ventas", font=ff(9),
                 bg=C["header"], fg=C["header_dim"],
                 cursor="hand2", padx=10).pack(side="left")

        suc_frame = tk.Frame(center, bg=C["header2"], padx=10, pady=4)
        suc_frame.pack(side="left", padx=8)
        tk.Label(suc_frame, text=f"🏪  {self.location['name']} ∨", font=ff(9),
                 bg=C["header2"], fg=C["header_text"]).pack()

        # Derecha: cajero + reloj
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

        # Panel izquierdo (productos)
        self.left_panel = tk.Frame(body, bg=C["bg"])
        self.left_panel.pack(side="left", fill="both", expand=True)

        # Separador
        tk.Frame(body, bg=C["border"], width=1).pack(side="left", fill="y")

        # Panel derecho (ticket)
        self.right_panel = tk.Frame(body, bg=C["surface"], width=360)
        self.right_panel.pack(side="right", fill="y")
        self.right_panel.pack_propagate(False)

        self._build_left(self.left_panel)
        self._build_ticket(self.right_panel)

    # ────────────────────────────────────────────────────────────
    #  LEFT PANEL (búsqueda + categorías + productos)
    # ────────────────────────────────────────────────────────────
    def _build_left(self, parent):
        # Barra de búsqueda
        search_frame = tk.Frame(parent, bg=C["bg"])
        search_frame.pack(fill="x", padx=20, pady=16)

        # Campo búsqueda
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
        self.entry_search.insert(0, "")

        # Placeholder
        self.entry_search.bind("<FocusIn>", self._search_focus_in)
        self.entry_search.bind("<FocusOut>", self._search_focus_out)
        self.entry_search.bind("<Return>", self._on_search_enter)

        # Botón scanner
        scan_btn = tk.Label(entry_wrap, text="⌘K", font=ff(9),
                            bg=C["bg2"], fg=C["text2"], padx=8, pady=4)
        scan_btn.pack(side="right", padx=8)

        tk.Label(search_frame, text="", bg=C["bg"], width=1).pack(side="left")

        # Botón scanner QR
        scan_icon = tk.Label(search_frame, text="📷", font=ff(14),
                             bg=C["surface"], padx=12, pady=8,
                             cursor="hand2",
                             highlightthickness=1, highlightbackground=C["border2"])
        scan_icon.pack(side="left")

        # Chips de categorías
        cat_frame = tk.Frame(parent, bg=C["bg"])
        cat_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.cat_buttons = {}
        for cat in CATEGORIES:
            cat_icons = {
                "Todos": "", "Quesos": "🧀", "Carnes Frías": "🥩",
                "Vinos": "🍷", "Panadería": "🥖", "Dulces": "🍬", "Aceites": "🫒"
            }
            icon = cat_icons.get(cat, "")
            label = f"{icon} {cat}".strip() if icon else cat

            btn = tk.Label(
                cat_frame,
                text=label,
                font=ff(9, "bold"),
                padx=12, pady=6,
                cursor="hand2",
                relief="flat"
            )
            btn.pack(side="left", padx=(0, 6))
            btn.bind("<Button-1>", lambda e, c=cat: self._select_category(c))
            self.cat_buttons[cat] = btn

        self._update_cat_buttons()

        # Grid de productos
        grid_frame = tk.Frame(parent, bg=C["bg"])
        grid_frame.pack(fill="both", expand=True, padx=20)

        # Scrollable canvas para cards
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

    def _search_focus_in(self, e):
        self.entry_search.config(fg=C["text"])
        # Actualizar borde
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

        # Configurar grid
        for c in range(COLS):
            self.prod_inner.columnconfigure(c, weight=1, uniform="col")

    def _make_card(self, p, row, col):
        is_out = p["stock"] <= 0
        is_low = 0 < p["stock"] <= 3

        card = tk.Frame(
            self.prod_inner,
            bg=C["surface"],
            padx=0, pady=0,
            cursor="hand2" if not is_out else "arrow",
            highlightthickness=1,
            highlightbackground=C["border"]
        )
        card.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")

        inner = tk.Frame(card, bg=C["surface"], padx=14, pady=12)
        inner.pack(fill="both", expand=True)

        # Stock badge (top-right)
        badge_row = tk.Frame(inner, bg=C["surface"])
        badge_row.pack(fill="x")

        emoji_lbl = tk.Label(badge_row, text=p.get("emoji", "📦"),
                             font=ff(22), bg=C["surface"])
        emoji_lbl.pack(side="left")

        if is_out:
            badge = tk.Label(badge_row, text="Agotado", font=ff(7, "bold"),
                             bg=C["chip_red"], fg=C["red"], padx=6, pady=2)
            badge.pack(side="right", anchor="n")
        elif is_low:
            badge = tk.Label(badge_row, text=f"Quedan {p['stock']}", font=ff(7, "bold"),
                             bg=C["chip_amber"], fg=C["amber"], padx=6, pady=2)
            badge.pack(side="right", anchor="n")
        else:
            badge = tk.Label(badge_row, text=f"{p['stock']} disp.", font=ff(7),
                             bg=C["surface"], fg=C["text3"])
            badge.pack(side="right", anchor="n")

        # SKU
        tk.Label(inner, text=p.get("sku", ""), font=fm(8),
                 bg=C["surface"], fg=C["text3"], anchor="w").pack(fill="x", pady=(6,0))

        # Nombre
        name_lbl = tk.Label(inner, text=p["name"], font=ff(10, "bold"),
                            bg=C["surface"], fg=C["text"] if not is_out else C["text3"],
                            anchor="w", wraplength=160, justify="left")
        name_lbl.pack(fill="x")

        # Precio
        price_frame = tk.Frame(inner, bg=C["surface"])
        price_frame.pack(fill="x", pady=(8, 0))

        price_lbl = tk.Label(price_frame,
                             text=f"${p['price']:,.2f}",
                             font=ff(13, "bold"),
                             bg=C["surface"],
                             fg=C["green"] if not is_out else C["text3"])
        price_lbl.pack(side="left")

        tk.Label(price_frame, text=f"/{p.get('unit','pza')}", font=ff(8),
                 bg=C["surface"], fg=C["text3"]).pack(side="left", padx=(2,0), pady=(3,0))

        # Hover effect & click
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
        # Header ticket
        t_header = tk.Frame(parent, bg=C["surface"])
        t_header.pack(fill="x", padx=20, pady=16)

        tk.Label(t_header, text="Ticket", font=ff(16, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")

        self.lbl_items_count = tk.Label(t_header, text="",
                                         font=ff(8, "bold"),
                                         bg=C["green_pale"], fg=C["green"],
                                         padx=8, pady=3)
        self.lbl_items_count.pack(side="right")

        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x")

        # Lista de items (scrollable)
        cart_wrap = tk.Frame(parent, bg=C["surface"])
        cart_wrap.pack(fill="both", expand=True)

        self.cart_canvas = tk.Canvas(cart_wrap, bg=C["surface"], highlightthickness=0)
        self.cart_canvas.pack(fill="both", expand=True)

        self.cart_inner = tk.Frame(self.cart_canvas, bg=C["surface"])
        self._cart_window = self.cart_canvas.create_window((0,0), window=self.cart_inner, anchor="nw")

        self.cart_inner.bind("<Configure>", lambda e: self.cart_canvas.configure(
            scrollregion=self.cart_canvas.bbox("all")))
        self.cart_canvas.bind("<Configure>", lambda e: self.cart_canvas.itemconfig(
            self._cart_window, width=e.width))

        # Totales
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x")

        totals = tk.Frame(parent, bg=C["surface"])
        totals.pack(fill="x", side="bottom")

        totals_inner = tk.Frame(totals, bg=C["surface"], padx=20, pady=12)
        totals_inner.pack(fill="x")

        # Subtotal
        r_sub = tk.Frame(totals_inner, bg=C["surface"])
        r_sub.pack(fill="x", pady=2)
        tk.Label(r_sub, text="Subtotal", font=ff(9), bg=C["surface"], fg=C["text2"]).pack(side="left")
        self.lbl_subtotal = tk.Label(r_sub, text="$0.00", font=fm(9),
                                      bg=C["surface"], fg=C["text2"])
        self.lbl_subtotal.pack(side="right")

        # IVA
        r_tax = tk.Frame(totals_inner, bg=C["surface"])
        r_tax.pack(fill="x", pady=2)
        tk.Label(r_tax, text="IVA 16%", font=ff(9), bg=C["surface"], fg=C["text2"]).pack(side="left")
        self.lbl_tax = tk.Label(r_tax, text="$0.00", font=fm(9),
                                 bg=C["surface"], fg=C["text2"])
        self.lbl_tax.pack(side="right")

        tk.Frame(totals_inner, bg=C["border"], height=1).pack(fill="x", pady=8)

        # Total grande
        r_total = tk.Frame(totals_inner, bg=C["surface"])
        r_total.pack(fill="x")
        tk.Label(r_total, text="TOTAL", font=ff(12, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        self.lbl_total = tk.Label(r_total, text="$0.00", font=fm(20, "bold"),
                                   bg=C["surface"], fg=C["text"])
        self.lbl_total.pack(side="right")

        # Método de pago
        pay_frame = tk.Frame(totals, bg=C["surface"], padx=20, pady=8)
        pay_frame.pack(fill="x")

        self.btn_efectivo = tk.Label(pay_frame, text="💵  Efectivo",
                                      font=ff(9, "bold"), padx=20, pady=8,
                                      cursor="hand2", relief="flat")
        self.btn_efectivo.pack(side="left", fill="x", expand=True, padx=(0,4))

        self.btn_tarjeta = tk.Label(pay_frame, text="💳  Tarjeta",
                                     font=ff(9, "bold"), padx=20, pady=8,
                                     cursor="hand2", relief="flat")
        self.btn_tarjeta.pack(side="left", fill="x", expand=True, padx=(4,0))

        self.btn_efectivo.bind("<Button-1>", lambda e: self._set_payment("efectivo"))
        self.btn_tarjeta.bind("<Button-1>", lambda e: self._set_payment("tarjeta"))
        self._update_pay_btns()

        # Botón Cobrar
        btn_area = tk.Frame(totals, bg=C["surface"])
        btn_area.pack(fill="x", padx=20, pady=(4, 16))

        self.btn_cobrar_canvas = tk.Canvas(btn_area, bg=C["surface"],
                                           height=50, highlightthickness=0)
        self.btn_cobrar_canvas.pack(fill="x")

        self.btn_cobrar_canvas.bind("<Button-1>", lambda e: self._process_sale() if getattr(self, "_last_cobrar_enabled", False) else None)
        # Redibujar cuando el canvas tenga tamaño real
        self.btn_cobrar_canvas.bind("<Configure>", lambda e: self._draw_cobrar_btn(
            getattr(self, "_last_cobrar_text", "$0.00"),
            enabled=getattr(self, "_last_cobrar_enabled", False)
        ))
        self._last_cobrar_text = "$0.00"
        self._last_cobrar_enabled = False

        # Binds globales
        self.bind_all("<F1>", lambda e: self.entry_search.focus_set())
        self.bind_all("<F2>", lambda e: self._process_sale())
        self.bind_all("<F3>", lambda e: self._clear_cart())
        self.bind_all("<Escape>", lambda e: (self.search_var.set(""), self.entry_search.focus_set()))

    def _draw_cobrar_btn(self, amount_text, enabled=True):
        self._last_cobrar_text = amount_text
        self._last_cobrar_enabled = enabled
        c = self.btn_cobrar_canvas
        c.delete("all")
        w = c.winfo_width()
        if w < 10:
            return  # Aún no tiene tamaño, el <Configure> lo volverá a llamar
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
            tk.Label(empty_frame, text="Agrega productos para comenzar la venta",
                     font=ff(9), bg=C["surface"], fg=C["text3"],
                     wraplength=200, justify="center").pack()
            return

        for i, item in enumerate(self.cart):
            p = item["product"]
            item_frame = tk.Frame(self.cart_inner, bg=C["surface"],
                                  padx=16, pady=10)
            item_frame.pack(fill="x")

            # Row 1: emoji + nombre + precio
            r1 = tk.Frame(item_frame, bg=C["surface"])
            r1.pack(fill="x")

            tk.Label(r1, text=p.get("emoji", "📦"), font=ff(14),
                     bg=C["surface"]).pack(side="left", padx=(0, 8))

            info = tk.Frame(r1, bg=C["surface"])
            info.pack(side="left", fill="x", expand=True)

            name_truncated = p["name"][:22] + "…" if len(p["name"]) > 22 else p["name"]
            tk.Label(info, text=name_truncated, font=ff(9, "bold"),
                     bg=C["surface"], fg=C["text"], anchor="w").pack(fill="x")

            price_row = tk.Frame(info, bg=C["surface"])
            price_row.pack(fill="x")
            tk.Label(price_row, text=f"${p['price']:,.2f}", font=fm(8),
                     bg=C["surface"], fg=C["text2"]).pack(side="left")
            tk.Label(price_row, text=f"c/u · SKU: {p.get('sku','')}", font=ff(7),
                     bg=C["surface"], fg=C["text3"]).pack(side="left", padx=4)

            tk.Label(r1, text=f"${item['subtotal']:,.2f}",
                     font=fm(10, "bold"), bg=C["surface"], fg=C["text"]).pack(side="right")

            # Row 2: controles qty
            r2 = tk.Frame(item_frame, bg=C["surface"])
            r2.pack(fill="x", pady=(6, 0))

            # Botón eliminar
            del_btn = tk.Label(r2, text="Eliminar", font=ff(8),
                               bg=C["surface"], fg=C["text3"],
                               cursor="hand2")
            del_btn.pack(side="left")
            del_btn.bind("<Button-1>", lambda e, idx=i: self._remove_item(idx))

            # Controles cantidad
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

            # Separador
            if i < len(self.cart) - 1:
                tk.Frame(self.cart_inner, bg=C["border"], height=1).pack(fill="x", padx=16)

        # Scroll al fondo
        self.cart_canvas.update_idletasks()
        self.cart_canvas.yview_moveto(1.0)

    def _update_totals(self):
        subtotal = sum(i["subtotal"] for i in self.cart)
        tax      = subtotal * 0.16
        total    = subtotal + tax
        count    = sum(i["qty"] for i in self.cart)

        self.lbl_subtotal.config(text=f"${subtotal:,.2f}")
        self.lbl_tax.config(text=f"${tax:,.2f}")
        self.lbl_total.config(text=f"${total:,.2f}")

        if count > 0:
            self.lbl_items_count.config(text=f"{count} artículos")
        else:
            self.lbl_items_count.config(text="")

        total_text = f"${total:,.2f}"
        has_cart   = bool(self.cart)
        # Guardar estado y forzar redibujado tras layout
        self._last_cobrar_text    = total_text
        self._last_cobrar_enabled = has_cart
        self.after(20, lambda: self._draw_cobrar_btn(total_text, enabled=has_cart))

    # ────────────────────────────────────────────────────────────
    #  CART OPERATIONS
    # ────────────────────────────────────────────────────────────
    def _add_to_cart(self, product):
        # Verificar stock en tiempo real
        stock_actual = self.db.get_stock(product["id"])
        if stock_actual <= 0:
            Toast(self, f"{product['name']} está agotado", "error")
            return

        existing = next((i for i in self.cart if i["product"]["id"] == product["id"]), None)
        if existing:
            if existing["qty"] >= stock_actual:
                Toast(self, f"Solo hay {stock_actual} disponibles", "warning")
                return
            existing["qty"] += 1
            existing["subtotal"] = existing["qty"] * existing["product"]["price"]
        else:
            self.cart.append({
                "product": product,
                "qty": 1,
                "subtotal": product["price"]
            })

        self._render_cart()
        self._update_totals()
        Toast(self, f"+ {product['name']}", "success", 1200)

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
        item["subtotal"] = new_qty * item["product"]["price"]
        self._render_cart()
        self._update_totals()

    def _remove_item(self, idx):
        name = self.cart[idx]["product"]["name"]
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
        folio = f"#{FOLIO_COUNTER[0]}"

        # Snapshot del carrito antes de limpiar
        cart_snapshot = list(self.cart)

        # Descontar stock de la BD
        for item in self.cart:
            self.db.update_stock(item["product"]["id"], -item["qty"])

        # Guardar venta en BD
        self.db.save_sale(
            folio, self.cart, total, subtotal, tax,
            payment, self.user["name"], self.location["name"]
        )

        # Limpiar carrito ANTES de mostrar modal
        self.cart.clear()
        self._render_cart()
        self._update_totals()
        self._load_products()

        # Mostrar modal según método de pago
        if payment == "tarjeta":
            self._show_terminal_modal(folio, total, subtotal, tax, cart_snapshot)
        else:
            self._show_success_modal(folio, total, subtotal, tax, cart_snapshot, payment)

    def _reset_for_new_sale(self):
        """Deja la app lista para una nueva venta."""
        self.search_var.set("")
        self.active_category.set("Todos")
        self._update_cat_buttons()
        self._load_products()
        self.entry_search.focus_set()

    def _show_terminal_modal(self, folio, total, subtotal, tax, cart_snapshot):
        """Modal para pago con tarjeta — simula conexión con terminal."""
        dlg = tk.Toplevel(self)
        dlg.title("Terminal")
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()

        w, h = 400, 340
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        inner = tk.Frame(dlg, bg=C["surface"])
        inner.pack(fill="both", expand=True, padx=36, pady=36)

        # Ícono terminal
        tk.Label(inner, text="💳", font=ff(40), bg=C["surface"]).pack()
        tk.Label(inner, text="Conexión con el Pointer",
                 font=ff(15, "bold"), bg=C["surface"], fg=C["text"]).pack(pady=(12, 6))
        tk.Label(inner, text=f"Total a cobrar: ${total:,.2f}",
                 font=fm(12, "bold"), bg=C["surface"], fg=C["green"]).pack()
        tk.Label(inner, text="Pase su tarjeta en el terminal...",
                 font=ff(9), bg=C["surface"], fg=C["text3"]).pack(pady=(8, 24))

        # Barra de progreso animada
        prog_frame = tk.Frame(inner, bg=C["border"], height=4)
        prog_frame.pack(fill="x")
        prog_bar = tk.Frame(prog_frame, bg=C["green"], height=4, width=0)
        prog_bar.place(x=0, y=0, relheight=1)

        btn = tk.Button(inner, text="✓  Confirmar pago",
                        font=ff(11, "bold"),
                        bg=C["green"], fg="white",
                        activebackground=C["green_hover"],
                        relief="flat", bd=0, cursor="hand2",
                        command=lambda: [dlg.destroy(), self._reset_for_new_sale()])
        btn.pack(fill="x", ipady=12, pady=(20, 0))

        # Animación de barra
        def animate(step=0):
            try:
                pct = min(step / 60, 1.0)
                prog_bar.place(x=0, y=0, relheight=1,
                               width=int(prog_frame.winfo_width() * pct))
                if step < 60:
                    dlg.after(50, lambda: animate(step + 1))
            except: pass
        dlg.after(100, animate)

        dlg.bind("<Return>", lambda e: [dlg.destroy(), self._reset_for_new_sale()])

    def _show_success_modal(self, folio, total, subtotal, tax, cart_snapshot, payment):
        """Modal de venta exitosa en efectivo."""
        dlg = tk.Toplevel(self)
        dlg.title("Venta Exitosa")
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()

        w, h = 420, 540
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        # Header
        hdr = tk.Frame(dlg, bg=C["surface"])
        hdr.pack(fill="x", padx=24, pady=16)
        tk.Label(hdr, text="¡Listo!", font=ff(18, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        close_lbl = tk.Label(hdr, text="✕", font=ff(14),
                             bg=C["surface"], fg=C["text3"], cursor="hand2")
        close_lbl.pack(side="right")
        close_lbl.bind("<Button-1>", lambda e: [dlg.destroy(), self._reset_for_new_sale()])

        # Check circle
        chk_frame = tk.Frame(dlg, bg=C["surface"])
        chk_frame.pack(pady=4)
        chk_circle = tk.Frame(chk_frame, bg=C["border"], width=64, height=64)
        chk_circle.pack()
        chk_circle.pack_propagate(False)
        tk.Label(chk_circle, text="✓", font=ff(26, "bold"),
                 bg=C["border"], fg=C["text"]).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(dlg, text="¡Venta Exitosa!", font=ff(15, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(pady=(8, 2))
        tk.Label(dlg,
                 text=f"Ticket {folio} · {datetime.now().strftime('%d %b %Y · %I:%M %p')}",
                 font=ff(8), bg=C["surface"], fg=C["text3"]).pack()

        # Items
        items_bg = tk.Frame(dlg, bg=C["bg2"])
        items_bg.pack(fill="x", padx=20, pady=12)
        items_inner = tk.Frame(items_bg, bg=C["bg2"], padx=14, pady=10)
        items_inner.pack(fill="x")
        for item in cart_snapshot:
            r = tk.Frame(items_inner, bg=C["bg2"])
            r.pack(fill="x", pady=1)
            name = f"{item['product'].get('emoji','')} {item['product']['name']} ×{item['qty']}"
            tk.Label(r, text=name, font=ff(9), bg=C["bg2"], fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        # Totales
        t_frame = tk.Frame(dlg, bg=C["surface"])
        t_frame.pack(fill="x", padx=36, pady=(0, 8))
        for label, value in [("Subtotal", f"${subtotal:,.2f}"), ("IVA 16%", f"${tax:,.2f}")]:
            r = tk.Frame(t_frame, bg=C["surface"])
            r.pack(fill="x")
            tk.Label(r, text=label, font=ff(9), bg=C["surface"], fg=C["text2"]).pack(side="left")
            tk.Label(r, text=value, font=fm(9), bg=C["surface"], fg=C["text2"]).pack(side="right")
        tk.Frame(t_frame, bg=C["border"], height=1).pack(fill="x", pady=6)
        r_t = tk.Frame(t_frame, bg=C["surface"])
        r_t.pack(fill="x")
        tk.Label(r_t, text="Total", font=ff(11, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        tk.Label(r_t, text=f"${total:,.2f}", font=fm(13, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="right")
        r_m = tk.Frame(t_frame, bg=C["surface"])
        r_m.pack(fill="x")
        tk.Label(r_m, text="Método", font=ff(9),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")
        tk.Label(r_m, text="💵 Efectivo", font=ff(9),
                 bg=C["surface"], fg=C["text"]).pack(side="right")

        # Botón imprimir / enviar
        btn_row = tk.Frame(dlg, bg=C["surface"])
        btn_row.pack(fill="x", padx=20, pady=(4, 4))
        tk.Button(btn_row, text="🖨  Imprimir", font=ff(9),
                  bg=C["surface"], fg=C["text"], relief="solid", bd=1,
                  padx=12, pady=7, cursor="hand2").pack(side="left", fill="x", expand=True, padx=(0,5))
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
        nueva_btn.pack(fill="x", padx=20, pady=(4, 20), ipady=12)
        nueva_btn.focus_set()

        dlg.bind("<Return>", lambda e: close_and_reset())
        dlg.bind("<Escape>", lambda e: close_and_reset())

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
        if len(visible) == 1 and visible[0]["stock"] > 0:
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
                now = datetime.now().strftime("lun %d de %b. %I:%M %p")
                try:
                    self.lbl_clock.config(text=now)
                except:
                    break
                time.sleep(30)
        threading.Thread(target=tick, daemon=True).start()
        # Inicial
        now = datetime.now().strftime("lun %d de %b. %I:%M %p")
        self.lbl_clock.config(text=now)

    def on_close(self):
        self.db.close()
        self.destroy()


# ════════════════════════════════════════════════════════════════
#  LOGIN WINDOW
# ════════════════════════════════════════════════════════════════

# Usuarios del sistema (usuario: contraseña, nombre_display)
SYSTEM_USERS = {
    "prueba":  ("prueba",  "Usuario Prueba"),
    "maria":   ("maria123","María G."),
    "admin":   ("admin",   "Administrador"),
}

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
        # Fondo superior decorativo
        top_bg = tk.Frame(self, bg=C["header"], height=180)
        top_bg.pack(fill="x")
        top_bg.pack_propagate(False)

        # Logo centrado
        logo_outer = tk.Frame(top_bg, bg="#2A5240", width=72, height=72)
        logo_outer.place(relx=0.5, rely=0.42, anchor="center")
        logo_outer.pack_propagate(False)
        tk.Label(logo_outer, text="LC", font=ff(22, "bold"),
                 bg="#2A5240", fg="white").place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(top_bg, text="La Casita", font=ff(18, "bold"),
                 bg=C["header"], fg=C["header_text"]).place(relx=0.5, rely=0.72, anchor="center")
        tk.Label(top_bg, text="Caja", font=ff(8),
                 bg=C["header"], fg=C["header_dim"]).place(relx=0.5, rely=0.88, anchor="center")

        # Tarjeta de login
        card = tk.Frame(self, bg=C["surface"], padx=36, pady=32)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Iniciar sesión", font=ff(15, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(card, text="Ingresa tus credenciales para continuar",
                 font=ff(9), bg=C["surface"], fg=C["text3"]).pack(anchor="w", pady=(2, 20))

        # Usuario
        tk.Label(card, text="Usuario", font=ff(9, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w")
        user_wrap = tk.Frame(card, bg=C["surface"],
                             highlightthickness=1, highlightbackground=C["border2"])
        user_wrap.pack(fill="x", pady=(4, 14))
        self.entry_user = tk.Entry(user_wrap, font=ff(11),
                                   bg=C["surface"], fg=C["text"],
                                   insertbackground=C["green"],
                                   relief="flat", bd=0)
        self.entry_user.pack(fill="x", padx=12, pady=10)
        self.entry_user.bind("<FocusIn>",  lambda e: user_wrap.config(highlightbackground=C["green_mid"], highlightthickness=2))
        self.entry_user.bind("<FocusOut>", lambda e: user_wrap.config(highlightbackground=C["border2"], highlightthickness=1))
        self.entry_user.bind("<Return>",   lambda e: self.entry_pass.focus_set())

        # Contraseña
        tk.Label(card, text="Contraseña", font=ff(9, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w")
        pass_wrap = tk.Frame(card, bg=C["surface"],
                             highlightthickness=1, highlightbackground=C["border2"])
        pass_wrap.pack(fill="x", pady=(4, 6))
        self.entry_pass = tk.Entry(pass_wrap, font=ff(11),
                                   bg=C["surface"], fg=C["text"],
                                   insertbackground=C["green"],
                                   show="●", relief="flat", bd=0)
        self.entry_pass.pack(fill="x", padx=12, pady=10)
        self.entry_pass.bind("<FocusIn>",  lambda e: pass_wrap.config(highlightbackground=C["green_mid"], highlightthickness=2))
        self.entry_pass.bind("<FocusOut>", lambda e: pass_wrap.config(highlightbackground=C["border2"], highlightthickness=1))
        self.entry_pass.bind("<Return>",   lambda e: self._do_login())

        # Error label
        self.lbl_error = tk.Label(card, text="", font=ff(9),
                                   bg=C["surface"], fg=C["red"])
        self.lbl_error.pack(anchor="w", pady=(0, 12))

        # Botón entrar
        login_btn = tk.Button(card, text="Entrar",
                              font=ff(12, "bold"),
                              bg=C["green"], fg="white",
                              activebackground=C["green_hover"],
                              relief="flat", bd=0, cursor="hand2",
                              command=self._do_login)
        login_btn.pack(fill="x", ipady=12)

        # Hint
        tk.Label(card, text="usuario: prueba  ·  contraseña: prueba",
                 font=ff(8), bg=C["surface"], fg=C["text3"]).pack(pady=(14, 0))

        self.entry_user.focus_set()

    def _do_login(self):
        username = self.entry_user.get().strip().lower()
        password = self.entry_pass.get()

        if username in SYSTEM_USERS:
            stored_pass, display_name = SYSTEM_USERS[username]
            if password == stored_pass:
                self._logged_user = {"id": username, "name": display_name, "role": "cajero"}
                self.destroy()
                return

        self.lbl_error.config(text="Usuario o contraseña incorrectos")
        self.entry_pass.delete(0, tk.END)
        self.entry_pass.focus_set()

    def get_user(self):
        return self._logged_user


# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Pantalla de login
    login = LoginWindow()
    login.mainloop()

    user = login.get_user()
    if not user:
        # Cerró sin hacer login
        exit(0)

    # Lanzar caja con el usuario autenticado
    app = CajaApp(logged_user=user)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
