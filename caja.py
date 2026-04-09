"""
La Casita Delicatessen — Sistema de Caja v4
Rediseño visual · Imágenes reales desde URL · Neon PostgreSQL · Zebra TC52
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime
import os
import io
import urllib.request
import urllib.error

# ── Pillow para imágenes ────────────────────────────────────────
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[IMG] Pillow no disponible — pip install pillow")

# ── psycopg2 ────────────────────────────────────────────────────
try:
    import psycopg2
    import psycopg2.extras
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# ── Configuración ────────────────────────────────────────────────
DB_URL = "postgresql://neondb_owner:npg_M0gYeTvqAS6F@ep-rapid-wildflower-an0psjmg-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# ── PALETA ───────────────────────────────────────────────────────
C = {
    "bg":           "#F7F4EF",
    "bg2":          "#EDEAE3",
    "surface":      "#FFFFFF",
    "surface2":     "#FAFAF8",
    "border":       "#E8E3DA",
    "border2":      "#D0C9BE",
    "text":         "#1C1A17",
    "text2":        "#6B6459",
    "text3":        "#A8A09A",
    "green":        "#1B4332",
    "green_hover":  "#2D6A4F",
    "green_mid":    "#40916C",
    "green_light":  "#74C69D",
    "green_pale":   "#D8F3DC",
    "amber":        "#92400E",
    "amber_bg":     "#FEF3C7",
    "red":          "#991B1B",
    "red_bg":       "#FEE2E2",
    "header":       "#0D2818",
    "header2":      "#163420",
    "header_text":  "#E9F2EC",
    "header_dim":   "#6B9E7A",
    "card_bg":      "#FFFFFF",
    "card_hover":   "#F5F2EC",
    "chip_active":  "#1B4332",
    "chip_text":    "#FFFFFF",
    "chip_idle":    "#FFFFFF",
    "chip_idle_fg": "#6B6459",
    "img_bg":       "#F0EDE8",
    "tag_green":    "#D8F3DC",
    "tag_green_fg": "#1B4332",
    "tag_amber":    "#FEF3C7",
    "tag_amber_fg": "#92400E",
    "tag_red":      "#FEE2E2",
    "tag_red_fg":   "#991B1B",
}

F_BRAND = "Georgia"     # Serif para el logo / titulares
F_UI    = "Segoe UI"    # UI principal
F_MONO  = "Consolas"    # Precios / monospaced

def _f(size=10, weight="normal", family=None):
    return (family or F_UI, size, weight)

def _fm(size=10, weight="normal"):
    return (F_MONO, size, weight)

def _fb(size=10):
    return (F_BRAND, size, "bold")


# ── Caché de imágenes ────────────────────────────────────────────
_img_cache: dict = {}
_img_lock = threading.Lock()

def load_image_async(url: str, size: tuple, callback):
    """Descarga y redimensiona una imagen en hilo background, luego llama callback(PhotoImage)."""
    if not PIL_AVAILABLE:
        callback(None)
        return

    key = (url, size)
    with _img_lock:
        if key in _img_cache:
            callback(_img_cache[key])
            return

    def _fetch():
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                data = resp.read()
            img = Image.open(io.BytesIO(data)).convert("RGBA")

            # Recorte cuadrado centrado
            w, h = img.size
            side = min(w, h)
            left = (w - side) // 2
            top  = (h - side) // 2
            img = img.crop((left, top, left + side, top + side))
            img = img.resize(size, Image.LANCZOS)

            # Esquinas redondeadas
            mask = Image.new("L", size, 0)
            draw = ImageDraw.Draw(mask)
            r = 12
            draw.rounded_rectangle([0, 0, size[0]-1, size[1]-1], radius=r, fill=255)
            img.putalpha(mask)

            photo = ImageTk.PhotoImage(img)
            with _img_lock:
                _img_cache[key] = photo
            callback(photo)
        except Exception as e:
            callback(None)

    threading.Thread(target=_fetch, daemon=True).start()


def make_placeholder(size: tuple, color: str = "#E8E3DA") -> "ImageTk.PhotoImage | None":
    if not PIL_AVAILABLE:
        return None
    img = Image.new("RGBA", size, color + "FF")
    draw = ImageDraw.Draw(img)
    # Grid lines decorativas
    for i in range(0, size[0], 20):
        draw.line([(i, 0), (i, size[1])], fill=color[:-2] + "30" if len(color) == 7 else "#00000010", width=1)
    photo = ImageTk.PhotoImage(img)
    return photo


# ── Datos mock ───────────────────────────────────────────────────
MOCK_PRODUCTS = [
    {"id": 1,  "codigo_barras": "QSO-001", "nombre": "Queso Manchego",       "precio_venta": 189.00, "stock_actual": 24, "stock_minimo": 5, "categoria": "Quesos",       "imagen_url": None},
    {"id": 2,  "codigo_barras": "CRN-002", "nombre": "Jamón Serrano",         "precio_venta": 320.00, "stock_actual": 5,  "stock_minimo": 5, "categoria": "Carnes Frías", "imagen_url": None},
    {"id": 3,  "codigo_barras": "VIN-003", "nombre": "Vino Tinto Reserva",    "precio_venta": 285.00, "stock_actual": 12, "stock_minimo": 5, "categoria": "Vinos",        "imagen_url": None},
    {"id": 4,  "codigo_barras": "PAN-004", "nombre": "Pan Baguette",          "precio_venta":  45.00, "stock_actual": 20, "stock_minimo": 5, "categoria": "Panadería",    "imagen_url": None},
    {"id": 5,  "codigo_barras": "ACE-005", "nombre": "Aceite de Oliva",       "precio_venta": 198.00, "stock_actual":  9, "stock_minimo": 5, "categoria": "Aceites",      "imagen_url": None},
    {"id": 6,  "codigo_barras": "DLC-006", "nombre": "Chocolate Belga 70%",   "precio_venta": 125.00, "stock_actual":  3, "stock_minimo": 5, "categoria": "Dulces",       "imagen_url": None},
    {"id": 7,  "codigo_barras": "QSO-007", "nombre": "Queso Brie",            "precio_venta": 165.00, "stock_actual":  7, "stock_minimo": 5, "categoria": "Quesos",       "imagen_url": None},
    {"id": 8,  "codigo_barras": "CRN-008", "nombre": "Salami Italiano",       "precio_venta": 145.00, "stock_actual":  0, "stock_minimo": 5, "categoria": "Carnes Frías", "imagen_url": None},
]
MOCK_USER     = {"id": 2, "name": "Cajero 1", "role": "cajero"}
MOCK_LOCATION = {"id": "L01", "name": "Sucursal Centro"}
FOLIO_COUNTER = [0]

SYSTEM_USERS = {
    "prueba": ("prueba",   "Usuario Prueba", None),
    "maria":  ("maria123", "María G.",       None),
    "admin":  ("admin",    "Administrador",  None),
}

CAT_ICONS = {
    "Todos": "◈", "Abarrotes": "🌾", "Bebidas": "🥤", "Lácteos": "🥛",
    "Limpieza": "✦", "Botanas": "◇", "Panadería": "◎", "Carnes frías": "◈",
    "Higiene": "✧", "Quesos": "◈", "Vinos": "◎", "Dulces": "◇",
    "Aceites": "◆", "Otros": "◈",
}


# ════════════════════════════════════════════════════════════════
#  DB MANAGER
# ════════════════════════════════════════════════════════════════
class DBManager:
    def __init__(self):
        self.conn      = None
        self.connected = False
        self._connect()

    def _connect(self):
        if not DB_AVAILABLE:
            return
        try:
            self.conn = psycopg2.connect(DB_URL, connect_timeout=8)
            self.conn.autocommit = False
            self.connected = True
            self._sync_folio_counter()
        except Exception as e:
            print(f"[DB] {e}")

    def _sync_folio_counter(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT folio FROM ventas WHERE canal='caja' AND folio LIKE 'CAJA-%' ORDER BY id DESC LIMIT 1")
            row = cur.fetchone()
            if row:
                try: FOLIO_COUNTER[0] = int(row[0].split("-")[1])
                except: pass
        except: pass

    def _ensure_connection(self):
        if not self.connected: return False
        try:
            self.conn.cursor().execute("SELECT 1")
            return True
        except:
            try:
                self.conn = psycopg2.connect(DB_URL, connect_timeout=5)
                self.conn.autocommit = False
                return True
            except:
                self.connected = False
                return False

    def get_products(self, search="", category="Todos"):
        if not self._ensure_connection():
            return self._filter_mock(search, category)
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            q = """
                SELECT p.id, p.codigo_barras, p.nombre, p.precio_venta,
                       p.stock_actual, p.stock_minimo, c.nombre AS categoria,
                       p.imagen_url
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
            return [dict(r) for r in cur.fetchall()]
        except Exception as e:
            try: self.conn.rollback()
            except: pass
            return self._filter_mock(search, category)

    def get_product_by_barcode(self, barcode):
        if not self._ensure_connection():
            return next((p for p in MOCK_PRODUCTS if p["codigo_barras"].lower() == barcode.lower()), None)
        try:
            cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT p.id, p.codigo_barras, p.nombre, p.precio_venta,
                       p.stock_actual, p.stock_minimo, c.nombre AS categoria, p.imagen_url
                FROM productos p
                LEFT JOIN categorias c ON c.id = p.categoria_id
                WHERE p.activo=TRUE AND LOWER(p.codigo_barras)=LOWER(%s)
            """, (barcode,))
            row = cur.fetchone()
            return dict(row) if row else None
        except: return None

    def get_stock(self, product_id):
        if not self._ensure_connection():
            p = next((x for x in MOCK_PRODUCTS if x["id"] == product_id), None)
            return p["stock_actual"] if p else 0
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT stock_actual FROM productos WHERE id=%s", (product_id,))
            row = cur.fetchone()
            return row[0] if row else 0
        except: return 0

    def get_categories(self):
        if not self._ensure_connection():
            return ["Quesos","Carnes Frías","Vinos","Panadería","Dulces","Aceites"]
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT DISTINCT c.nombre FROM categorias c
                JOIN productos p ON p.categoria_id=c.id
                WHERE c.activo=TRUE AND p.activo=TRUE ORDER BY c.nombre
            """)
            return [r[0] for r in cur.fetchall()]
        except: return []

    def save_sale(self, folio, cart, total, subtotal, tax, payment, cashier, location, usuario_id=None):
        if not self._ensure_connection():
            return None, "sin_conexion"
        import json
        items_json = json.dumps([{
            "producto_id": i["product"]["id"],
            "cantidad": i["qty"],
            "precio_unitario": float(i["product"]["precio_venta"])
        } for i in cart])
        uid = usuario_id or self._get_or_create_user_id(cashier)
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT registrar_venta(%s,%s,%s,%s,%s::jsonb)",
                        (folio, "caja", uid, payment, items_json))
            venta_id = cur.fetchone()[0]
            self.conn.commit()
            return venta_id, None
        except psycopg2.errors.RaiseException as e:
            try: self.conn.rollback()
            except: pass
            return None, str(e).split("\n")[0]
        except Exception as e:
            try: self.conn.rollback()
            except: pass
            return None, str(e)

    def _get_or_create_user_id(self, display_name):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM usuarios WHERE nombre=%s AND activo=TRUE LIMIT 1", (display_name,))
            row = cur.fetchone()
            if row: return row[0]
            cur.execute("SELECT id FROM usuarios WHERE rol='cajero' AND activo=TRUE ORDER BY id LIMIT 1")
            row = cur.fetchone()
            return row[0] if row else None
        except: return None

    def _filter_mock(self, search, category):
        r = MOCK_PRODUCTS
        if search: r = [p for p in r if search.lower() in p["nombre"].lower()]
        if category and category != "Todos": r = [p for p in r if p.get("categoria") == category]
        return r

    def close(self):
        if self.conn:
            try: self.conn.close()
            except: pass


# ════════════════════════════════════════════════════════════════
#  BARCODE SCANNER
# ════════════════════════════════════════════════════════════════
class BarcodeScanner:
    TIMEOUT_MS = 120
    MIN_LENGTH  = 4

    def __init__(self, root, callback):
        self.root = root; self.callback = callback
        self._buffer = []; self._last_t = 0
        root.bind_all("<KeyPress>", self._on_key, add="+")

    def _on_key(self, event):
        now = time.time() * 1000
        if now - self._last_t > self.TIMEOUT_MS and self._buffer:
            self._buffer = []
        self._last_t = now
        if event.keysym == "Return":
            s = "".join(self._buffer).strip(); self._buffer = []
            if len(s) >= self.MIN_LENGTH: self.callback(s)
        elif event.char and event.char.isprintable():
            self._buffer.append(event.char)


# ════════════════════════════════════════════════════════════════
#  TOAST
# ════════════════════════════════════════════════════════════════
class Toast(tk.Toplevel):
    def __init__(self, master, message, type_="success", duration=1800):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        colors = {"success": (C["green"], "#74C69D"), "error": (C["red"], "#FCA5A5"), "warning": (C["amber"], "#FCD34D")}
        bg, accent = colors.get(type_, (C["green"], "#74C69D"))
        outer = tk.Frame(self, bg=accent, padx=1, pady=1)
        outer.pack()
        inner = tk.Frame(outer, bg=bg, padx=20, pady=11)
        inner.pack()
        icon = {"success":"✓","error":"✕","warning":"⚠"}.get(type_,"✓")
        tk.Label(inner, text=f"{icon}  {message}", font=_f(10,"bold"), bg=bg, fg="white").pack()
        self.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() - self.winfo_width()) // 2
        y = master.winfo_y() + master.winfo_height() - 80
        self.geometry(f"+{x}+{y}")
        self._fade_in(duration)

    def _fade_in(self, dur, step=0):
        a = min(1.0, step * 0.15)
        try:
            self.attributes("-alpha", a)
            if a < 1.0: self.after(25, lambda: self._fade_in(dur, step+1))
            else: self.after(dur, self._fade_out)
        except: pass

    def _fade_out(self, step=8):
        a = max(0.0, step * 0.125)
        try:
            self.attributes("-alpha", a)
            if a > 0: self.after(35, lambda: self._fade_out(step-1))
            else: self.destroy()
        except: pass


# ════════════════════════════════════════════════════════════════
#  PRODUCT CARD WIDGET
# ════════════════════════════════════════════════════════════════
class ProductCard(tk.Frame):
    IMG_SIZE = (140, 110)

    def __init__(self, parent, product: dict, on_click, **kwargs):
        super().__init__(parent, bg=C["card_bg"], cursor="arrow",
                         highlightthickness=1, highlightbackground=C["border"],
                         **kwargs)
        self.product    = product
        self._on_click  = on_click
        self._photo     = None
        self._destroyed = False

        stock     = product.get("stock_actual", 0)
        min_stock = product.get("stock_minimo", 5)
        self.is_out = stock <= 0
        self.is_low = 0 < stock <= min_stock

        self._build()
        self._load_image()
        self._bind_events()

    def _build(self):
        p = self.product
        stock = p.get("stock_actual", 0)

        # ── Área imagen ──────────────────────────────────────────
        self.img_frame = tk.Frame(self, bg=C["img_bg"],
                                  width=self.IMG_SIZE[0], height=self.IMG_SIZE[1])
        self.img_frame.pack(fill="x")
        self.img_frame.pack_propagate(False)

        self.img_label = tk.Label(self.img_frame, bg=C["img_bg"],
                                  text="", cursor="hand2" if not self.is_out else "arrow")
        self.img_label.place(relx=0.5, rely=0.5, anchor="center")

        # Badge stock (superpuesto sobre imagen)
        if self.is_out:
            badge_bg, badge_fg, badge_txt = C["tag_red"], C["tag_red_fg"], "Agotado"
        elif self.is_low:
            badge_bg, badge_fg, badge_txt = C["tag_amber"], C["tag_amber_fg"], f"{stock} restantes"
        else:
            badge_bg, badge_fg, badge_txt = C["tag_green"], C["tag_green_fg"], f"{stock} en stock"

        badge = tk.Label(self.img_frame, text=badge_txt, font=_f(7,"bold"),
                         bg=badge_bg, fg=badge_fg, padx=7, pady=2)
        badge.place(relx=1.0, rely=0.0, anchor="ne", x=-6, y=6)

        # ── Info ────────────────────────────────────────────────
        info = tk.Frame(self, bg=C["card_bg"], padx=12, pady=10)
        info.pack(fill="x")

        # Categoría
        cat = p.get("categoria", "")
        tk.Label(info, text=cat.upper(), font=_f(7,"bold"),
                 bg=C["card_bg"], fg=C["green_mid"]).pack(anchor="w")

        # Nombre
        nombre = p.get("nombre", "")
        tk.Label(info, text=nombre, font=_f(10,"bold"),
                 bg=C["card_bg"],
                 fg=C["text"] if not self.is_out else C["text3"],
                 wraplength=155, justify="left", anchor="w").pack(fill="x", pady=(1,0))

        # Precio + SKU
        bottom = tk.Frame(info, bg=C["card_bg"])
        bottom.pack(fill="x", pady=(6,0))

        price = float(p.get("precio_venta", 0))
        price_color = C["green"] if not self.is_out else C["text3"]
        tk.Label(bottom, text=f"${price:,.0f}", font=_fm(13,"bold"),
                 bg=C["card_bg"], fg=price_color).pack(side="left")

        sku = p.get("codigo_barras","")
        if sku:
            tk.Label(bottom, text=sku, font=_f(7),
                     bg=C["card_bg"], fg=C["text3"]).pack(side="right", anchor="s", pady=1)

    def _load_image(self):
        url = self.product.get("imagen_url")
        if url and PIL_AVAILABLE and url.startswith("http"):
            # Mostrar placeholder mientras carga
            ph = make_placeholder(self.IMG_SIZE, C["img_bg"])
            if ph:
                self.img_label.config(image=ph)
                self._photo = ph

            def on_loaded(photo):
                if self._destroyed: return
                if photo:
                    self.img_label.config(image=photo,
                        bg=C["img_bg"] if not self.is_out else "#F5F0EA")
                    self._photo = photo
                else:
                    self.img_label.config(text="📦", font=_f(28), image="")

            load_image_async(url, self.IMG_SIZE, on_loaded)
        else:
            # Fallback emoji
            emoji_map = {
                "Quesos":"🧀","Carnes Frías":"🥩","Vinos":"🍷","Panadería":"🥖",
                "Aceites":"🫒","Dulces":"🍬","Bebidas":"🥤","Botanas":"🍿",
                "Lácteos":"🥛","Abarrotes":"🌾",
            }
            cat = self.product.get("categoria","")
            e = emoji_map.get(cat, "📦")
            self.img_label.config(text=e, font=_f(30), image="")

    def _bind_events(self):
        widgets = [self, self.img_frame, self.img_label]
        for child in self.winfo_children():
            widgets.append(child)
            for subchild in child.winfo_children():
                widgets.append(subchild)

        for w in widgets:
            if not self.is_out:
                w.bind("<Enter>",    self._on_enter, add="+")
                w.bind("<Leave>",    self._on_leave, add="+")
            w.bind("<Button-1>", self._clicked,  add="+")

    def _on_enter(self, e):
        self.config(highlightbackground=C["green_mid"], highlightthickness=2,
                    bg=C["card_hover"])

    def _on_leave(self, e):
        self.config(highlightbackground=C["border"], highlightthickness=1,
                    bg=C["card_bg"])

    def _clicked(self, e):
        if not self.is_out:
            self._on_click(self.product)

    def destroy(self):
        self._destroyed = True
        super().destroy()


# ════════════════════════════════════════════════════════════════
#  MAIN APP
# ════════════════════════════════════════════════════════════════
class CajaApp(tk.Tk):
    COLS = 4

    def __init__(self, logged_user=None):
        super().__init__()
        self.title("La Casita — Punto de Venta")
        self.geometry("1440x880")
        self.minsize(1200, 720)
        self.configure(bg=C["bg"])

        self.user     = logged_user or MOCK_USER
        self.location = MOCK_LOCATION
        self.cart     = []
        self.pay_var  = tk.StringVar(value="efectivo")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)
        self._search_after = None
        self.active_category = tk.StringVar(value="Todos")

        self.db = DBManager()
        self._db_status = "Conectado" if self.db.connected else "Offline"

        self._categories = ["Todos"] + self.db.get_categories()
        if len(self._categories) <= 1:
            self._categories = ["Todos","Abarrotes","Bebidas","Lácteos","Botanas","Panadería"]

        self._build_ui()
        self._load_products()
        self._start_clock()
        self.scanner = BarcodeScanner(self, self._on_barcode_scanned)

    # ── Barcode ─────────────────────────────────────────────────
    def _on_barcode_scanned(self, code):
        p = self.db.get_product_by_barcode(code)
        if p: self._add_to_cart(p)
        else: Toast(self, f"Código no encontrado: {code}", "error", 2500)

    # ════════════════════════════════════════════════════════════
    #  UI BUILD
    # ════════════════════════════════════════════════════════════
    def _build_ui(self):
        self._build_header()
        self._build_body()

    # ── HEADER ──────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=C["header"], height=58)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Left — brand
        left = tk.Frame(hdr, bg=C["header"])
        left.pack(side="left", padx=22, pady=0)
        left.pack_configure(pady=0)

        logo_wrap = tk.Frame(left, bg="#2A6647", padx=10, pady=5)
        logo_wrap.pack(side="left")
        tk.Label(logo_wrap, text="LC", font=_fb(12),
                 bg="#2A6647", fg="white").pack()

        sep = tk.Frame(left, bg="#2D4A38", width=1)
        sep.pack(side="left", fill="y", padx=14, pady=10)

        brand = tk.Frame(left, bg=C["header"])
        brand.pack(side="left")
        tk.Label(brand, text="La Casita", font=(F_BRAND, 13, "bold"),
                 bg=C["header"], fg=C["header_text"]).pack(anchor="w")
        tk.Label(brand, text="PUNTO DE VENTA", font=_f(6,"bold"),
                 bg=C["header"], fg=C["header_dim"]).pack(anchor="w")

        # Center — search
        center = tk.Frame(hdr, bg=C["header"])
        center.place(relx=0.42, rely=0.5, anchor="center")

        search_outer = tk.Frame(center, bg="#FFFFFF", highlightthickness=0)
        search_outer.pack()
        search_inner = tk.Frame(search_outer, bg="#FFFFFF")
        search_inner.pack(padx=1, pady=1)

        tk.Label(search_inner, text="⌕", font=_f(13), bg="#FFFFFF",
                 fg=C["text3"]).pack(side="left", padx=(10,2))
        self.entry_search = tk.Entry(
            search_inner, textvariable=self.search_var,
            font=_f(10), bg="#FFFFFF", fg=C["text"],
            insertbackground=C["green"], relief="flat", bd=0, width=30)
        self.entry_search.pack(side="left", pady=9, padx=(0,10))
        self.entry_search.bind("<Return>", self._on_search_enter)
        self.entry_search.bind("<FocusIn>",  lambda e: search_outer.config(bg=C["green_mid"]))
        self.entry_search.bind("<FocusOut>", lambda e: search_outer.config(bg=C["border2"]))

        search_outer.config(bg=C["border2"])

        # Right — info
        right = tk.Frame(hdr, bg=C["header"])
        right.pack(side="right", padx=22)

        self.lbl_clock = tk.Label(right, text="", font=_f(9),
                                   bg=C["header"], fg=C["header_dim"])
        self.lbl_clock.pack(side="right", padx=(12,0))

        sep2 = tk.Frame(right, bg="#2D4A38", width=1)
        sep2.pack(side="right", fill="y", pady=12, padx=8)

        user_frame = tk.Frame(right, bg=C["header"])
        user_frame.pack(side="right")
        tk.Label(user_frame, text=f"  {self.user['name']}",
                 font=_f(9,"bold"), bg=C["header"], fg=C["header_text"]).pack(anchor="e")
        status_color = C["green_light"] if self.db.connected else C["amber"]
        tk.Label(user_frame,
                 text=f"● {self._db_status}  ·  {self.location['name']}",
                 font=_f(7), bg=C["header"], fg=status_color).pack(anchor="e")

        # Keyboard shortcuts hint
        sep3 = tk.Frame(right, bg="#2D4A38", width=1)
        sep3.pack(side="right", fill="y", pady=12, padx=8)
        hints = tk.Frame(right, bg=C["header"])
        hints.pack(side="right")
        for k, v in [("F1","Buscar"), ("F2","Cobrar"), ("F3","Limpiar")]:
            r = tk.Frame(hints, bg=C["header"])
            r.pack(side="left", padx=6)
            tk.Label(r, text=k, font=_f(7,"bold"), bg="#2A3E30",
                     fg=C["header_dim"], padx=4, pady=1).pack(side="left")
            tk.Label(r, text=f" {v}", font=_f(7), bg=C["header"],
                     fg=C["header_dim"]).pack(side="left")

    # ── BODY ────────────────────────────────────────────────────
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

    # ── LEFT ────────────────────────────────────────────────────
    def _build_left(self, parent):
        # Category chips
        cat_bar = tk.Frame(parent, bg=C["bg"])
        cat_bar.pack(fill="x", padx=20, pady=(14,0))

        # Transaction info
        tx_frame = tk.Frame(cat_bar, bg=C["bg"])
        tx_frame.pack(side="right")
        FOLIO_COUNTER[0] += 0  # ensure synced
        tx_num = FOLIO_COUNTER[0] + 1
        tk.Label(tx_frame, text=f"Transacción #{tx_num:04d}  ·  Estación 01",
                 font=_f(8), bg=C["bg"], fg=C["text3"]).pack()

        chips_wrap = tk.Frame(parent, bg=C["bg"])
        chips_wrap.pack(fill="x", padx=20, pady=(10,4))

        self.chip_scroll = tk.Frame(chips_wrap, bg=C["bg"])
        self.chip_scroll.pack(fill="x")

        self.cat_buttons = {}
        for cat in self._categories:
            icon  = CAT_ICONS.get(cat, "◈")
            label = f"{icon}  {cat}"
            btn = tk.Label(self.chip_scroll, text=label, font=_f(9,"bold"),
                           padx=14, pady=6, cursor="hand2")
            btn.pack(side="left", padx=(0,6), pady=2)
            btn.bind("<Button-1>", lambda e, c=cat: self._select_category(c))
            self.cat_buttons[cat] = btn
        self._update_cat_buttons()

        # Divider
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", padx=20)

        # Products grid
        grid_outer = tk.Frame(parent, bg=C["bg"])
        grid_outer.pack(fill="both", expand=True, padx=20, pady=12)

        self.prod_canvas = tk.Canvas(grid_outer, bg=C["bg"], highlightthickness=0)
        vsb = tk.Scrollbar(grid_outer, orient="vertical",
                           command=self.prod_canvas.yview)
        vsb.pack(side="right", fill="y")
        self.prod_canvas.pack(side="left", fill="both", expand=True)
        self.prod_canvas.configure(yscrollcommand=vsb.set)

        self.prod_inner = tk.Frame(self.prod_canvas, bg=C["bg"])
        self._prod_win = self.prod_canvas.create_window((0,0), window=self.prod_inner, anchor="nw")

        self.prod_inner.bind("<Configure>", lambda e: self.prod_canvas.configure(
            scrollregion=self.prod_canvas.bbox("all")))
        self.prod_canvas.bind("<Configure>", lambda e: self.prod_canvas.itemconfig(
            self._prod_win, width=e.width))
        self.prod_canvas.bind_all("<MouseWheel>", lambda e: self.prod_canvas.yview_scroll(
            int(-1*(e.delta/120)), "units"))

        # Keyboard
        self.bind_all("<F1>", lambda e: self.entry_search.focus_set())
        self.bind_all("<F2>", lambda e: self._process_sale())
        self.bind_all("<F3>", lambda e: self._clear_cart())
        self.bind_all("<Escape>", lambda e: (self.search_var.set(""),
                                              self.entry_search.focus_set()))

    def _select_category(self, cat):
        self.active_category.set(cat)
        self._update_cat_buttons()
        self._load_products()

    def _update_cat_buttons(self):
        active = self.active_category.get()
        for cat, btn in self.cat_buttons.items():
            if cat == active:
                btn.config(bg=C["chip_active"], fg=C["chip_text"],
                           highlightthickness=0)
            else:
                btn.config(bg=C["chip_idle"], fg=C["chip_idle_fg"],
                           highlightthickness=1)
                try: btn.config(highlightbackground=C["border2"])
                except: pass

    # ── PRODUCT GRID ────────────────────────────────────────────
    def _render_products(self, products):
        for w in self.prod_inner.winfo_children():
            w.destroy()

        if not products:
            wrap = tk.Frame(self.prod_inner, bg=C["bg"])
            wrap.pack(fill="both", expand=True, pady=80)
            tk.Label(wrap, text="Sin resultados", font=_f(13),
                     bg=C["bg"], fg=C["text3"]).pack()
            tk.Label(wrap, text="Intenta con otro término o categoría",
                     font=_f(9), bg=C["bg"], fg=C["text3"]).pack(pady=4)
            return

        COLS = self.COLS
        for i, p in enumerate(products):
            r, c = divmod(i, COLS)
            card = ProductCard(self.prod_inner, p, self._add_to_cart)
            card.grid(row=r, column=c, padx=7, pady=7, sticky="nsew")

        for c in range(COLS):
            self.prod_inner.columnconfigure(c, weight=1, uniform="col")

    # ── TICKET ──────────────────────────────────────────────────
    def _build_ticket(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        t_hdr = tk.Frame(parent, bg=C["surface"], padx=20, pady=14)
        t_hdr.grid(row=0, column=0, sticky="ew")

        left_h = tk.Frame(t_hdr, bg=C["surface"])
        left_h.pack(side="left")
        tk.Label(left_h, text="Ticket actual", font=_f(13,"bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w")
        self.lbl_customer = tk.Label(left_h, text="Cliente: Invitado",
                                      font=_f(8), bg=C["surface"], fg=C["text3"])
        self.lbl_customer.pack(anchor="w")

        right_h = tk.Frame(t_hdr, bg=C["surface"])
        right_h.pack(side="right")
        self.lbl_items_badge = tk.Label(right_h, text="",
                                         font=_f(8,"bold"),
                                         bg=C["green_pale"], fg=C["green"],
                                         padx=8, pady=3)
        self.lbl_items_badge.pack(side="top", anchor="e")
        clr = tk.Label(right_h, text="Limpiar", font=_f(8),
                       bg=C["surface"], fg=C["text3"], cursor="hand2")
        clr.pack(side="top", anchor="e", pady=(4,0))
        clr.bind("<Button-1>", lambda e: self._clear_cart())

        tk.Frame(parent, bg=C["border"], height=1).grid(row=0, column=0, sticky="sew", pady=(0,0))

        # Cart list
        cart_wrap = tk.Frame(parent, bg=C["surface"])
        cart_wrap.grid(row=1, column=0, sticky="nsew")

        self.cart_canvas = tk.Canvas(cart_wrap, bg=C["surface"], highlightthickness=0)
        csb = tk.Scrollbar(cart_wrap, orient="vertical", command=self.cart_canvas.yview)
        csb.pack(side="right", fill="y")
        self.cart_canvas.pack(side="left", fill="both", expand=True)
        self.cart_canvas.configure(yscrollcommand=csb.set)

        self.cart_inner = tk.Frame(self.cart_canvas, bg=C["surface"])
        self._cart_win = self.cart_canvas.create_window((0,0), window=self.cart_inner, anchor="nw")
        self.cart_inner.bind("<Configure>", lambda e: self.cart_canvas.configure(
            scrollregion=self.cart_canvas.bbox("all")))
        self.cart_canvas.bind("<Configure>", lambda e: self.cart_canvas.itemconfig(
            self._cart_win, width=e.width))

        # Footer
        foot = tk.Frame(parent, bg=C["surface"])
        foot.grid(row=2, column=0, sticky="ew")

        tk.Frame(foot, bg=C["border"], height=1).pack(fill="x")

        totals = tk.Frame(foot, bg=C["surface"], padx=20, pady=12)
        totals.pack(fill="x")

        for attr, label in [("lbl_subtotal","Subtotal"), ("lbl_tax","IVA (8%)")]:
            row = tk.Frame(totals, bg=C["surface"])
            row.pack(fill="x", pady=1)
            tk.Label(row, text=label, font=_f(9), bg=C["surface"],
                     fg=C["text2"]).pack(side="left")
            lbl = tk.Label(row, text="$0.00", font=_fm(9),
                           bg=C["surface"], fg=C["text2"])
            lbl.pack(side="right")
            setattr(self, attr, lbl)

        tk.Frame(totals, bg=C["border"], height=1).pack(fill="x", pady=6)

        total_row = tk.Frame(totals, bg=C["surface"])
        total_row.pack(fill="x")
        tk.Label(total_row, text="Total", font=_f(12,"bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        self.lbl_total = tk.Label(total_row, text="$0.00", font=_fm(18,"bold"),
                                   bg=C["surface"], fg=C["text"])
        self.lbl_total.pack(side="right")

        # Payment methods
        pay_row = tk.Frame(foot, bg=C["surface"], padx=20, pady=8)
        pay_row.pack(fill="x")

        self.btn_efectivo = tk.Label(pay_row, text="💵  Efectivo",
                                      font=_f(9,"bold"), padx=0, pady=9,
                                      cursor="hand2", anchor="center")
        self.btn_efectivo.pack(side="left", fill="x", expand=True,
                                padx=(0,5), pady=0)
        self.btn_efectivo.bind("<Button-1>", lambda e: self._set_payment("efectivo"))

        self.btn_tarjeta = tk.Label(pay_row, text="💳  Tarjeta",
                                     font=_f(9,"bold"), padx=0, pady=9,
                                     cursor="hand2", anchor="center")
        self.btn_tarjeta.pack(side="left", fill="x", expand=True, padx=(5,0))
        self.btn_tarjeta.bind("<Button-1>", lambda e: self._set_payment("tarjeta"))
        self._update_pay_btns()

        # Cobrar button
        btn_area = tk.Frame(foot, bg=C["surface"], padx=20, pady=2) 
        btn_area.pack(fill="x")
        
        self.cobrar_canvas = tk.Canvas(btn_area, bg=C["surface"],
                                        height=50, highlightthickness=0)
        self.cobrar_canvas.pack(fill="x")
        self.cobrar_canvas.bind("<Button-1>",  lambda e: self._process_sale()
                                 if self._cobrar_enabled else None)
        self.cobrar_canvas.bind("<Configure>", lambda e: self._draw_cobrar())
        self._cobrar_enabled = False
        self._cobrar_text    = "$0.00"

    def _draw_cobrar(self):
        c = self.cobrar_canvas; c.delete("all")
        w = c.winfo_width()
        if w < 10: return
        h, r = 50, 10
        fill = C["green"] if self._cobrar_enabled else C["text3"]
        c.create_arc(0,0,r*2,r*2, start=90, extent=90, fill=fill, outline=fill)
        c.create_arc(w-r*2,0,w,r*2, start=0, extent=90, fill=fill, outline=fill)
        c.create_arc(0,h-r*2,r*2,h, start=180, extent=90, fill=fill, outline=fill)
        c.create_arc(w-r*2,h-r*2,w,h, start=270, extent=90, fill=fill, outline=fill)
        c.create_rectangle(r,0,w-r,h, fill=fill, outline=fill)
        c.create_rectangle(0,r,w,h-r, fill=fill, outline=fill)
        label = f"Completar transacción  →  {self._cobrar_text}" if self._cobrar_enabled else "Completar transacción"
        c.create_text(w//2, h//2, text=label, fill="white",
                      font=(F_UI,11,"bold"), anchor="center")
        c.config(cursor="hand2" if self._cobrar_enabled else "arrow")

    def _set_payment(self, method):
        self.pay_var.set(method)
        self._update_pay_btns()

    def _update_pay_btns(self):
        sel = self.pay_var.get()
        if sel == "efectivo":
            self.btn_efectivo.config(bg=C["green"], fg="white",
                                     highlightthickness=0)
            self.btn_tarjeta.config(bg=C["bg2"], fg=C["text2"],
                                    highlightthickness=1,
                                    highlightbackground=C["border"])
        else:
            self.btn_tarjeta.config(bg=C["green"], fg="white",
                                    highlightthickness=0)
            self.btn_efectivo.config(bg=C["bg2"], fg=C["text2"],
                                     highlightthickness=1,
                                     highlightbackground=C["border"])

    # ── CART RENDER ─────────────────────────────────────────────
    def _render_cart(self):
        for w in self.cart_inner.winfo_children():
            w.destroy()

        if not self.cart:
            wrap = tk.Frame(self.cart_inner, bg=C["surface"])
            wrap.pack(fill="both", expand=True, pady=50, padx=20)
            tk.Label(wrap, text="🛒", font=_f(32), bg=C["surface"],
                     fg=C["border2"]).pack()
            tk.Label(wrap, text="Ticket vacío", font=_f(11,"bold"),
                     bg=C["surface"], fg=C["text3"]).pack(pady=(6,2))
            tk.Label(wrap, text="Agrega productos o escanea un código",
                     font=_f(8), bg=C["surface"], fg=C["text3"],
                     wraplength=200, justify="center").pack()
            return

        for i, item in enumerate(self.cart):
            self._render_cart_item(i, item)
            if i < len(self.cart) - 1:
                tk.Frame(self.cart_inner, bg=C["border"], height=1).pack(
                    fill="x", padx=16)

        self.cart_canvas.update_idletasks()
        self.cart_canvas.yview_moveto(1.0)

    def _render_cart_item(self, idx, item):
        p = item["product"]
        frame = tk.Frame(self.cart_inner, bg=C["surface"], padx=16, pady=10)
        frame.pack(fill="x")

        # Top row: image thumb + info + price
        top = tk.Frame(frame, bg=C["surface"])
        top.pack(fill="x")

        # Tiny thumbnail
        thumb = tk.Label(top, bg=C["img_bg"], width=5, text="", font=_f(16))
        thumb.pack(side="left", padx=(0,10))

        url = p.get("imagen_url")
        if url and PIL_AVAILABLE and url.startswith("http"):
            def on_thumb(ph, lbl=thumb):
                if ph:
                    lbl.config(image=ph, text="")
                    lbl._photo = ph
                else:
                    lbl.config(text=_cat_emoji(p))
            load_image_async(url, (44, 44), on_thumb)
        else:
            thumb.config(text=_cat_emoji(p))

        info = tk.Frame(top, bg=C["surface"])
        info.pack(side="left", fill="x", expand=True)

        nombre = p.get("nombre","")
        short = nombre[:24] + "…" if len(nombre) > 24 else nombre
        tk.Label(info, text=short, font=_f(9,"bold"),
                 bg=C["surface"], fg=C["text"], anchor="w").pack(fill="x")

        price = float(p.get("precio_venta",0))
        tk.Label(info, text=f"${price:,.2f} c/u",
                 font=_f(8), bg=C["surface"], fg=C["text3"],
                 anchor="w").pack(fill="x")

        tk.Label(top, text=f"${item['subtotal']:,.2f}", font=_fm(10,"bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="right", anchor="n", pady=2)

        # Bottom row: delete + qty controls
        bot = tk.Frame(frame, bg=C["surface"])
        bot.pack(fill="x", pady=(6,0))

        del_lbl = tk.Label(bot, text="Eliminar", font=_f(8),
                           bg=C["surface"], fg=C["text3"], cursor="hand2")
        del_lbl.pack(side="left")
        del_lbl.bind("<Button-1>", lambda e, i=idx: self._remove_item(i))

        # Qty stepper
        ctrl = tk.Frame(bot, bg=C["bg2"], highlightthickness=1,
                        highlightbackground=C["border"])
        ctrl.pack(side="right")

        minus = tk.Label(ctrl, text="  −  ", font=_f(11,"bold"),
                         bg=C["bg2"], fg=C["text"], cursor="hand2", pady=2)
        minus.pack(side="left")
        minus.bind("<Button-1>", lambda e, i=idx: self._change_qty(i, -1))

        tk.Label(ctrl, text=f"  {item['qty']}  ", font=_fm(10,"bold"),
                 bg=C["bg2"], fg=C["text"]).pack(side="left")

        plus = tk.Label(ctrl, text="  +  ", font=_f(11,"bold"),
                        bg=C["bg2"], fg=C["green"], cursor="hand2", pady=2)
        plus.pack(side="left")
        plus.bind("<Button-1>", lambda e, i=idx: self._change_qty(i, 1))

    def _update_totals(self):
        subtotal = sum(float(i["subtotal"]) for i in self.cart)
        tax      = round(subtotal * 0.08, 2)
        total    = round(subtotal + tax, 2)
        count    = sum(int(i["qty"]) for i in self.cart)

        self.lbl_subtotal.config(text=f"${subtotal:,.2f}")
        self.lbl_tax.config(text=f"${tax:,.2f}")
        self.lbl_total.config(text=f"${total:,.2f}", fg=C["green"] if self.cart else C["text"])
        self.lbl_items_badge.config(
            text=f"{count} artículo{'s' if count != 1 else ''}" if count else "")
        self._cobrar_text    = f"${total:,.2f}"
        self._cobrar_enabled = bool(self.cart)
        self.after(20, self._draw_cobrar)

    # ── CART OPS ────────────────────────────────────────────────
    def _add_to_cart(self, product):
        stock = self.db.get_stock(product["id"])
        if stock <= 0:
            Toast(self, f"{product['nombre']} está agotado", "error"); return
        existing = next((i for i in self.cart if i["product"]["id"] == product["id"]), None)
        if existing:
            if existing["qty"] >= stock:
                Toast(self, f"Solo hay {stock} en stock", "warning"); return
            existing["qty"] += 1
            existing["subtotal"] = existing["qty"] * float(existing["product"]["precio_venta"])
        else:
            self.cart.append({"product": product, "qty": 1,
                               "subtotal": float(product["precio_venta"])})
        self._render_cart()
        self._update_totals()
        Toast(self, f"+ {product['nombre'][:28]}", "success", 1200)

    def _change_qty(self, idx, delta):
        item = self.cart[idx]; nq = item["qty"] + delta
        if nq <= 0: self._remove_item(idx); return
        stock = self.db.get_stock(item["product"]["id"])
        if nq > stock: Toast(self, f"Solo hay {stock} en stock", "warning"); return
        item["qty"] = nq
        item["subtotal"] = nq * float(item["product"]["precio_venta"])
        self._render_cart(); self._update_totals()

    def _remove_item(self, idx):
        name = self.cart[idx]["product"]["nombre"]
        self.cart.pop(idx)
        self._render_cart(); self._update_totals()
        Toast(self, f"Eliminado: {name[:22]}", "warning", 1200)

    def _clear_cart(self):
        if not self.cart: return
        if messagebox.askyesno("Limpiar ticket", "¿Cancelar todos los artículos?"):
            self.cart.clear(); self._render_cart(); self._update_totals()

    # ── SALE ────────────────────────────────────────────────────
    def _process_sale(self):
        if not self.cart: return
        subtotal = sum(i["subtotal"] for i in self.cart)
        tax      = subtotal * 0.08
        total    = subtotal + tax
        payment  = self.pay_var.get()
        FOLIO_COUNTER[0] += 1
        folio = f"CAJA-{FOLIO_COUNTER[0]:06d}"
        cart_snapshot = [dict(i) for i in self.cart]

        venta_id, error = self.db.save_sale(
            folio, self.cart, total, subtotal, tax, payment,
            self.user["name"], self.location["name"],
            usuario_id=self.user.get("id") if isinstance(self.user.get("id"), int) else None
        )
        if error and error != "sin_conexion":
            messagebox.showerror("Error en la venta", f"No se pudo completar:\n{error}")
            FOLIO_COUNTER[0] -= 1; return

        self.cart.clear(); self._render_cart(); self._update_totals(); self._load_products()
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

    # ── MODALS ──────────────────────────────────────────────────
    def _modal_base(self, title, w=460, h=600):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.attributes("-topmost", True)
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")
        return dlg

    def _show_cash_modal(self, folio, total, subtotal, tax, cart_snapshot):
        dlg = self._modal_base("Cobro en Efectivo", 460, 640)

        hdr = tk.Frame(dlg, bg=C["green"], pady=22)
        hdr.pack(fill="x")
        tk.Label(hdr, text="💵", font=_f(32), bg=C["green"]).pack()
        tk.Label(hdr, text="Cobro en Efectivo", font=_f(15,"bold"),
                 bg=C["green"], fg="white").pack(pady=(4,0))
        tk.Label(hdr, text=f"{folio}  ·  {datetime.now().strftime('%d %b %Y  %H:%M')}",
                 font=_f(8), bg=C["green"], fg=C["green_pale"]).pack()

        body = tk.Frame(dlg, bg=C["surface"], padx=28, pady=14)
        body.pack(fill="both", expand=True)

        items_bg = tk.Frame(body, bg=C["bg2"])
        items_bg.pack(fill="x", pady=(0,10))
        for item in cart_snapshot:
            r = tk.Frame(items_bg, bg=C["bg2"])
            r.pack(fill="x", padx=12, pady=2)
            e = _cat_emoji(item["product"])
            nombre = item["product"].get("nombre","")
            tk.Label(r, text=f"{e} {nombre} ×{item['qty']}", font=_f(9),
                     bg=C["bg2"], fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=_fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        for lbl, val in [("Subtotal",f"${subtotal:,.2f}"),("IVA 8%",f"${tax:,.2f}")]:
            row = tk.Frame(body, bg=C["surface"]); row.pack(fill="x", pady=1)
            tk.Label(row, text=lbl, font=_f(9), bg=C["surface"], fg=C["text2"]).pack(side="left")
            tk.Label(row, text=val, font=_fm(9), bg=C["surface"], fg=C["text2"]).pack(side="right")
        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=6)
        r_t = tk.Frame(body, bg=C["surface"]); r_t.pack(fill="x")
        tk.Label(r_t, text="TOTAL", font=_f(13,"bold"), bg=C["surface"], fg=C["text"]).pack(side="left")
        tk.Label(r_t, text=f"${total:,.2f}", font=_fm(16,"bold"),
                 bg=C["surface"], fg=C["green"]).pack(side="right")

        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=10)
        tk.Label(body, text="Con cuánto paga el cliente:", font=_f(9,"bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w")

        cw = tk.Frame(body, bg=C["surface"], highlightthickness=2, highlightbackground=C["green_mid"])
        cw.pack(fill="x", pady=(4,0))
        tk.Label(cw, text="$", font=_fm(16,"bold"), bg=C["surface"], fg=C["text2"], padx=8).pack(side="left")
        cash_var = tk.StringVar()
        entry_cash = tk.Entry(cw, textvariable=cash_var, font=_fm(16,"bold"),
                              bg=C["surface"], fg=C["text"], insertbackground=C["green"],
                              relief="flat", bd=0, width=12, justify="right")
        entry_cash.pack(side="left", fill="x", expand=True, pady=12, padx=(0,12))
        entry_cash.focus_set()

        chf = tk.Frame(body, bg=C["surface"]); chf.pack(fill="x", pady=6)
        tk.Label(chf, text="Cambio:", font=_f(11,"bold"), bg=C["surface"], fg=C["text2"]).pack(side="left")
        lbl_change = tk.Label(chf, text="—", font=_fm(16,"bold"), bg=C["surface"], fg=C["text3"])
        lbl_change.pack(side="right")

        qf = tk.Frame(body, bg=C["surface"]); qf.pack(fill="x", pady=(2,8))
        tk.Label(qf, text="Rápidos:", font=_f(8), bg=C["surface"], fg=C["text3"]).pack(side="left", padx=(0,6))
        suggestions = [b for b in [20,50,100,200,500,1000] if b >= total][:4] or [500,1000]
        for amt in suggestions:
            b = tk.Label(qf, text=f"${int(amt):,}", font=_f(9,"bold"),
                         bg=C["bg2"], fg=C["text"], padx=10, pady=4, cursor="hand2")
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda e, a=amt: [cash_var.set(f"{a:.0f}"), _recalc()])

        btn_confirm = tk.Button(body, text="✓  Confirmar cobro", font=_f(12,"bold"),
                                bg=C["text3"], fg="white", activebackground=C["green_hover"],
                                relief="flat", bd=0, cursor="hand2", state="disabled",
                                command=lambda: _confirm())
        btn_confirm.pack(fill="x", ipady=13, pady=(4,4))
        tk.Button(body, text="Cancelar", font=_f(9), bg=C["surface"], fg=C["text3"],
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda: [dlg.destroy(), self._reset_for_new_sale()]).pack(fill="x", ipady=6)

        def _recalc(*a):
            try:
                paid = float(cash_var.get().replace(",",""))
                cambio = paid - total
                if cambio < 0:
                    lbl_change.config(text=f"-${abs(cambio):,.2f}", fg=C["red"])
                    btn_confirm.config(state="disabled", bg=C["text3"])
                else:
                    lbl_change.config(text=f"${cambio:,.2f}", fg=C["green"])
                    btn_confirm.config(state="normal", bg=C["green"])
            except:
                lbl_change.config(text="—", fg=C["text3"])
                btn_confirm.config(state="disabled", bg=C["text3"])

        def _confirm():
            try:
                paid = float(cash_var.get().replace(",",""))
                if paid < total: return
            except: return
            dlg.destroy()
            self._show_cash_success(folio, total, subtotal, tax, cart_snapshot, paid, paid-total)

        cash_var.trace_add("write", _recalc)
        entry_cash.bind("<Return>", lambda e: _confirm())
        dlg.bind("<Escape>", lambda e: [dlg.destroy(), self._reset_for_new_sale()])

    def _show_cash_success(self, folio, total, subtotal, tax, cart_snapshot, paid, cambio):
        dlg = self._modal_base("¡Venta Exitosa!", 420, 520)
        hdr = tk.Frame(dlg, bg=C["surface"]); hdr.pack(fill="x", padx=24, pady=16)
        tk.Label(hdr, text="¡Listo!", font=_f(18,"bold"), bg=C["surface"], fg=C["text"]).pack(side="left")

        chk = tk.Frame(dlg, bg=C["green_pale"], width=72, height=72); chk.pack(); chk.pack_propagate(False)
        tk.Label(chk, text="✓", font=_f(28,"bold"), bg=C["green_pale"],
                 fg=C["green"]).place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(dlg, text="¡Venta Exitosa!", font=_f(15,"bold"), bg=C["surface"], fg=C["text"]).pack(pady=(8,2))
        tk.Label(dlg, text=f"{folio}  ·  {datetime.now().strftime('%d %b %Y  %H:%M')}",
                 font=_f(8), bg=C["surface"], fg=C["text3"]).pack()

        cf = tk.Frame(dlg, bg=C["green_pale"], pady=14); cf.pack(fill="x", padx=24, pady=12)
        tk.Label(cf, text="CAMBIO", font=_f(10,"bold"), bg=C["green_pale"], fg=C["green_mid"]).pack()
        tk.Label(cf, text=f"${cambio:,.2f}", font=_fm(26,"bold"), bg=C["green_pale"], fg=C["green"]).pack()
        tk.Label(cf, text=f"Recibido: ${paid:,.2f}  ·  Total: ${total:,.2f}",
                 font=_f(8), bg=C["green_pale"], fg=C["green_mid"]).pack()

        items_bg = tk.Frame(dlg, bg=C["bg2"]); items_bg.pack(fill="x", padx=24, pady=(0,8))
        ii = tk.Frame(items_bg, bg=C["bg2"], padx=12, pady=8); ii.pack(fill="x")
        for item in cart_snapshot:
            r = tk.Frame(ii, bg=C["bg2"]); r.pack(fill="x", pady=1)
            nombre = item["product"].get("nombre","")
            tk.Label(r, text=f"{_cat_emoji(item['product'])} {nombre} ×{item['qty']}",
                     font=_f(9), bg=C["bg2"], fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=_fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        def close(): dlg.destroy(); self._reset_for_new_sale()
        tk.Button(dlg, text="Nueva Venta", font=_f(12,"bold"),
                  bg=C["green"], fg="white", activebackground=C["green_hover"],
                  relief="flat", bd=0, cursor="hand2",
                  command=close).pack(fill="x", padx=24, pady=(0,20), ipady=12)
        dlg.bind("<Return>", lambda e: close())
        dlg.bind("<Escape>", lambda e: close())
        dlg.after(30000, lambda: (dlg.destroy(), self._reset_for_new_sale()) if dlg.winfo_exists() else None)

    def _show_card_modal(self, folio, total, subtotal, tax, cart_snapshot):
        dlg = self._modal_base("Cobro con Tarjeta", 440, 520)
        hdr = tk.Frame(dlg, bg="#1A2B4A", pady=22); hdr.pack(fill="x")
        tk.Label(hdr, text="💳", font=_f(32), bg="#1A2B4A").pack()
        tk.Label(hdr, text="Cobro con Tarjeta", font=_f(15,"bold"),
                 bg="#1A2B4A", fg="white").pack(pady=(4,0))
        tk.Label(hdr, text=f"${total:,.2f}", font=_fm(22,"bold"),
                 bg="#1A2B4A", fg="#7FC8F8").pack(pady=(4,0))

        body = tk.Frame(dlg, bg=C["surface"], padx=28, pady=14); body.pack(fill="both", expand=True)

        tf = tk.Frame(body, bg="#F0F4FA", pady=14); tf.pack(fill="x", pady=(0,10))
        tk.Label(tf, text="⬛", font=_f(28), bg="#F0F4FA", fg="#333").pack()
        tk.Label(tf, text="Terminal · Pago manual", font=_f(9,"bold"),
                 bg="#F0F4FA", fg="#1A2B4A").pack(pady=(6,2))
        tk.Label(tf, text="⚠  Confirma manualmente cuando el pago sea aprobado",
                 font=_f(8), bg="#F0F4FA", fg=C["amber"]).pack()

        items_bg = tk.Frame(body, bg=C["bg2"]); items_bg.pack(fill="x", pady=(0,8))
        for item in cart_snapshot:
            r = tk.Frame(items_bg, bg=C["bg2"]); r.pack(fill="x", padx=12, pady=2)
            nombre = item["product"].get("nombre","")
            tk.Label(r, text=f"{_cat_emoji(item['product'])} {nombre} ×{item['qty']}",
                     font=_f(9), bg=C["bg2"], fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=_fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        def _confirm(): dlg.destroy(); self._show_card_success(folio, total, subtotal, tax, cart_snapshot)
        tk.Button(body, text="✓  Pago Confirmado", font=_f(11,"bold"),
                  bg="#1A2B4A", fg="white", activebackground="#243D6A",
                  relief="flat", bd=0, cursor="hand2",
                  command=_confirm).pack(fill="x", ipady=13, pady=(8,4))
        tk.Button(body, text="Cancelar", font=_f(9), bg=C["surface"], fg=C["text3"],
                  relief="flat", bd=0, cursor="hand2",
                  command=lambda: [dlg.destroy(), self._reset_for_new_sale()]).pack(fill="x", ipady=6)
        dlg.bind("<Return>", lambda e: _confirm())
        dlg.bind("<Escape>", lambda e: [dlg.destroy(), self._reset_for_new_sale()])

    def _show_card_success(self, folio, total, subtotal, tax, cart_snapshot):
        dlg = self._modal_base("Pago Aprobado", 420, 460)
        hdr = tk.Frame(dlg, bg=C["surface"]); hdr.pack(fill="x", padx=24, pady=16)
        tk.Label(hdr, text="¡Listo!", font=_f(18,"bold"), bg=C["surface"], fg=C["text"]).pack(side="left")

        chk = tk.Frame(dlg, bg="#EEF2FF", width=72, height=72); chk.pack(); chk.pack_propagate(False)
        tk.Label(chk, text="✓", font=_f(28,"bold"), bg="#EEF2FF",
                 fg="#1A2B4A").place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(dlg, text="Pago con Tarjeta Aprobado", font=_f(15,"bold"),
                 bg=C["surface"], fg=C["text"]).pack(pady=(8,2))
        tk.Label(dlg, text=f"{folio}  ·  {datetime.now().strftime('%d %b %Y  %H:%M')}",
                 font=_f(8), bg=C["surface"], fg=C["text3"]).pack()

        tf = tk.Frame(dlg, bg="#EEF2FF", pady=10); tf.pack(fill="x", padx=24, pady=10)
        tk.Label(tf, text=f"${total:,.2f}", font=_fm(22,"bold"), bg="#EEF2FF", fg="#1A2B4A").pack()
        tk.Label(tf, text="💳  Tarjeta", font=_f(9), bg="#EEF2FF", fg="#4A6A9A").pack()

        items_bg = tk.Frame(dlg, bg=C["bg2"]); items_bg.pack(fill="x", padx=24, pady=(0,8))
        ii = tk.Frame(items_bg, bg=C["bg2"], padx=12, pady=8); ii.pack(fill="x")
        for item in cart_snapshot:
            r = tk.Frame(ii, bg=C["bg2"]); r.pack(fill="x", pady=1)
            nombre = item["product"].get("nombre","")
            tk.Label(r, text=f"{_cat_emoji(item['product'])} {nombre} ×{item['qty']}",
                     font=_f(9), bg=C["bg2"], fg=C["text"], anchor="w").pack(side="left")
            tk.Label(r, text=f"${item['subtotal']:,.2f}", font=_fm(9),
                     bg=C["bg2"], fg=C["text"]).pack(side="right")

        def close(): dlg.destroy(); self._reset_for_new_sale()
        tk.Button(dlg, text="Nueva Venta", font=_f(12,"bold"),
                  bg="#1A2B4A", fg="white", activebackground="#243D6A",
                  relief="flat", bd=0, cursor="hand2",
                  command=close).pack(fill="x", padx=24, pady=(0,20), ipady=12)
        dlg.bind("<Return>", lambda e: close())
        dlg.bind("<Escape>", lambda e: close())
        dlg.after(30000, lambda: (dlg.destroy(), self._reset_for_new_sale()) if dlg.winfo_exists() else None)

    # ── DATA ────────────────────────────────────────────────────
    def _load_products(self):
        products = self.db.get_products(self.search_var.get().strip(),
                                        self.active_category.get())
        self._render_products(products)

    def _on_search_change(self, *args):
        if self._search_after: self.after_cancel(self._search_after)
        self._search_after = self.after(250, self._load_products)

    def _on_search_enter(self, event):
        q = self.search_var.get().strip()
        if not q: return
        visible = self.db.get_products(q, self.active_category.get())
        if len(visible) == 1 and visible[0].get("stock_actual", 0) > 0:
            self._add_to_cart(visible[0])
            self.search_var.set("")

    # ── CLOCK ───────────────────────────────────────────────────
    def _start_clock(self):
        def tick():
            while True:
                now = datetime.now().strftime("%a %d %b  %H:%M")
                try: self.lbl_clock.config(text=now)
                except: break
                time.sleep(30)
        threading.Thread(target=tick, daemon=True).start()
        self.lbl_clock.config(text=datetime.now().strftime("%a %d %b  %H:%M"))

    def on_close(self):
        self.db.close(); self.destroy()


# ── Helper ───────────────────────────────────────────────────────
def _cat_emoji(product: dict) -> str:
    emoji_map = {
        "Quesos":"🧀","Carnes Frías":"🥩","Vinos":"🍷","Panadería":"🥖",
        "Aceites":"🫒","Dulces":"🍫","Bebidas":"🥤","Botanas":"🍿",
        "Lácteos":"🥛","Abarrotes":"🌾",
    }
    cat = product.get("categoria","")
    return emoji_map.get(cat, "📦")


# ════════════════════════════════════════════════════════════════
#  LOGIN
# ════════════════════════════════════════════════════════════════
class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("La Casita — Inicio de Sesión")
        self.resizable(False, False)
        self.configure(bg=C["header"])
        self._logged_user = None
        w, h = 420, 520
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        self._build()

    def _build(self):
        top = tk.Frame(self, bg=C["header"], height=180)
        top.pack(fill="x"); top.pack_propagate(False)

        logo = tk.Frame(top, bg="#2A6647", width=72, height=72)
        logo.place(relx=0.5, rely=0.4, anchor="center"); logo.pack_propagate(False)
        tk.Label(logo, text="LC", font=_fb(22), bg="#2A6647",
                 fg="white").place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(top, text="La Casita", font=(F_BRAND,18,"bold"),
                 bg=C["header"], fg=C["header_text"]).place(relx=0.5, rely=0.72, anchor="center")
        tk.Label(top, text="PUNTO DE VENTA", font=_f(7,"bold"),
                 bg=C["header"], fg=C["header_dim"]).place(relx=0.5, rely=0.88, anchor="center")

        card = tk.Frame(self, bg=C["surface"], padx=36, pady=32)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Iniciar sesión", font=_f(15,"bold"),
                 bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(card, text="Ingresa tus credenciales para continuar",
                 font=_f(9), bg=C["surface"], fg=C["text3"]).pack(anchor="w", pady=(2,20))

        for label, attr, show in [("Usuario","entry_user",""),("Contraseña","entry_pass","●")]:
            tk.Label(card, text=label, font=_f(9,"bold"),
                     bg=C["surface"], fg=C["text2"]).pack(anchor="w")
            wrap = tk.Frame(card, bg=C["surface"],
                            highlightthickness=1, highlightbackground=C["border2"])
            wrap.pack(fill="x", pady=(4,14))
            entry = tk.Entry(wrap, font=_f(11), bg=C["surface"], fg=C["text"],
                             insertbackground=C["green"], show=show, relief="flat", bd=0)
            entry.pack(fill="x", padx=12, pady=10)
            entry.bind("<FocusIn>",  lambda e, w=wrap: w.config(highlightbackground=C["green_mid"], highlightthickness=2))
            entry.bind("<FocusOut>", lambda e, w=wrap: w.config(highlightbackground=C["border2"], highlightthickness=1))
            setattr(self, attr, entry)

        self.entry_user.bind("<Return>", lambda e: self.entry_pass.focus_set())
        self.entry_pass.bind("<Return>", lambda e: self._do_login())

        self.lbl_error = tk.Label(card, text="", font=_f(9),
                                   bg=C["surface"], fg=C["red"])
        self.lbl_error.pack(anchor="w", pady=(0,12))

        tk.Button(card, text="Entrar", font=_f(12,"bold"),
                  bg=C["green"], fg="white", activebackground=C["green_hover"],
                  relief="flat", bd=0, cursor="hand2",
                  command=self._do_login).pack(fill="x", ipady=12)

        tk.Label(card, text="usuario: prueba  ·  contraseña: prueba",
                 font=_f(8), bg=C["surface"], fg=C["text3"]).pack(pady=(14,0))
        self.entry_user.focus_set()

    def _do_login(self):
        u = self.entry_user.get().strip().lower()
        p = self.entry_pass.get()
        if u in SYSTEM_USERS:
            stored_pass, display_name, db_id = SYSTEM_USERS[u]
            if p == stored_pass:
                self._logged_user = {"id": db_id, "name": display_name, "role": "cajero"}
                self.destroy(); return
        self.lbl_error.config(text="Usuario o contraseña incorrectos")
        self.entry_pass.delete(0, tk.END); self.entry_pass.focus_set()

    def get_user(self): return self._logged_user


# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    login = LoginWindow(); login.mainloop()
    user = login.get_user()
    if not user: exit(0)
    app = CajaApp(logged_user=user)
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
