"""
La Casita Delicatessen — Sistema de Caja
Aplicacion de escritorio para punto de venta
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from datetime import datetime

# ─── PALETA DE COLORES LA CASITA ──────────────────────────────────
C = {
    "bg":          "#F4F1EC",   # Fondo general, crema calido
    "surface":     "#FFFFFF",   # Superficies / cards
    "border":      "#DDD8CF",   # Bordes sutiles
    "text":        "#1C1A17",   # Texto principal
    "text2":       "#6B6358",   # Texto secundario
    "text3":       "#A8A099",   # Texto terciario / placeholder

    # Verde La Casita — primario
    "green":       "#2D6A4F",   # Verde oscuro principal
    "green_mid":   "#40916C",   # Verde medio
    "green_light": "#74C69D",   # Verde claro
    "green_bg":    "#D8F3DC",   # Verde fondo suave

    # Acentos
    "amber":       "#B45309",   # Ambar para alertas / cambio
    "amber_bg":    "#FEF3C7",

    "red":         "#B91C1C",   # Error / cancelar
    "red_bg":      "#FEE2E2",

    "blue":        "#1D4ED8",
    "blue_bg":     "#DBEAFE",

    # Header bar
    "header":      "#1A3A2A",   # Verde muy oscuro para barra superior
    "header_text": "#E8F5EE",

    # Fila alternada tabla
    "row_even":    "#FFFFFF",
    "row_odd":     "#F9F7F4",
    "row_sel":     "#D8F3DC",
    "row_sel_txt": "#1A3A2A",
}

FONT_FAMILY = "Segoe UI"
MONO_FAMILY = "Consolas"

def font(size=11, weight="normal", family=FONT_FAMILY):
    return (family, size, weight)

def mono(size=11, weight="normal"):
    return (MONO_FAMILY, size, weight)


# ─── DATOS MOCK (hasta conectar con API) ──────────────────────────
MOCK_PRODUCTS = [
    {"id": "P001", "barcode": "7501000001",  "name": "Queso Manchego 200g",          "price": 89.00,  "stock": 24, "category": "Lacteos",    "unit": "pza"},
    {"id": "P002", "barcode": "7501000002",  "name": "Jamon Serrano 100g",            "price": 65.00,  "stock": 18, "category": "Frios",      "unit": "pza"},
    {"id": "P003", "barcode": "7501000003",  "name": "Pan Artesanal Integral",        "price": 45.00,  "stock": 12, "category": "Panaderia",  "unit": "pza"},
    {"id": "P004", "barcode": "7501000004",  "name": "Aceite de Oliva Extra Virgen",  "price": 189.00, "stock": 9,  "category": "Abarrotes",  "unit": "pza"},
    {"id": "P005", "barcode": "7501000005",  "name": "Mermelada de Higo Artesanal",   "price": 72.00,  "stock": 15, "category": "Abarrotes",  "unit": "pza"},
    {"id": "P006", "barcode": "7501000006",  "name": "Vino Tinto Reserva 750ml",      "price": 320.00, "stock": 6,  "category": "Vinos",      "unit": "bot"},
    {"id": "P007", "barcode": "7501000007",  "name": "Salmon Ahumado 150g",           "price": 145.00, "stock": 8,  "category": "Frios",      "unit": "pza"},
    {"id": "P008", "barcode": "7501000008",  "name": "Galletas de Mantequilla",       "price": 38.00,  "stock": 30, "category": "Panaderia",  "unit": "pza"},
    {"id": "P009", "barcode": "7501000009",  "name": "Queso Parmesano Rallado 80g",   "price": 55.00,  "stock": 20, "category": "Lacteos",    "unit": "pza"},
    {"id": "P010", "barcode": "7501000010",  "name": "Pasta Fresca Tagliatelle",      "price": 48.00,  "stock": 14, "category": "Abarrotes",  "unit": "pza"},
    {"id": "P011", "barcode": "7501000011",  "name": "Cerveza Artesanal IPA 355ml",   "price": 58.00,  "stock": 40, "category": "Bebidas",    "unit": "bot"},
    {"id": "P012", "barcode": "7501000012",  "name": "Miel de Abeja Silvestre 250g",  "price": 95.00,  "stock": 11, "category": "Abarrotes",  "unit": "pza"},
    {"id": "P013", "barcode": "7501000013",  "name": "Chorizo Iberico 200g",          "price": 118.00, "stock": 7,  "category": "Frios",      "unit": "pza"},
    {"id": "P014", "barcode": "7501000014",  "name": "Agua Mineral 500ml",            "price": 22.00,  "stock": 60, "category": "Bebidas",    "unit": "bot"},
    {"id": "P015", "barcode": "7501000015",  "name": "Cafe de Especialidad 250g",     "price": 155.00, "stock": 9,  "category": "Bebidas",    "unit": "pza"},
]

MOCK_USER = {"id": "U01", "name": "Maria Lopez", "role": "cajero"}
MOCK_LOCATION = {"id": "L01", "name": "Casita 1 — Centro"}


# ═══════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ═══════════════════════════════════════════════════════════════════
class CajaApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("La Casita — Punto de Venta")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(bg=C["bg"])

        # Estado
        self.user = MOCK_USER
        self.location = MOCK_LOCATION
        self.cart = []          # [{product, qty, subtotal}]
        self.payment = "efectivo"
        self.products = list(MOCK_PRODUCTS)
        self.session_open = True
        self.folio_counter = 1

        self._build_ui()
        self._start_clock()

    # ── CONSTRUCCION UI ───────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_status_bar()
        self._build_body()

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["header"], height=52)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)

        # Marca
        brand = tk.Frame(hdr, bg=C["header"])
        brand.pack(side="left", padx=20, pady=12)

        tk.Label(brand, text="LA CASITA", font=font(15, "bold"),
                 bg=C["header"], fg=C["header_text"]).pack(side="left")
     

        sep = tk.Frame(hdr, bg="#3D6B50", width=1)
        sep.pack(side="left", fill="y", pady=10, padx=16)

        tk.Label(hdr, text="Punto de Venta", font=font(11),
                 bg=C["header"], fg="#9BC4AB").pack(side="left")

        # Info derecha
        right = tk.Frame(hdr, bg=C["header"])
        right.pack(side="right", padx=20)

        self.lbl_clock = tk.Label(right, text="", font=mono(12),
                                  bg=C["header"], fg="#74C69D")
        self.lbl_clock.pack(side="right", padx=12)

        sep2 = tk.Frame(right, bg="#3D6B50", width=1)
        sep2.pack(side="right", fill="y", pady=10)

        tk.Label(right, text=self.user["name"], font=font(11),
                 bg=C["header"], fg=C["header_text"]).pack(side="right", padx=12)

        tk.Label(right, text=self.location["name"], font=font(10),
                 bg=C["header"], fg="#9BC4AB").pack(side="right", padx=4)

    def _build_status_bar(self):
        bar = tk.Frame(self, bg=C["green"], height=30)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        self.lbl_session = tk.Label(
            bar,
            text="  Sesion activa  |  " + self.location["name"],
            font=font(9), bg=C["green"], fg=C["green_bg"],
            anchor="w"
        )
        self.lbl_session.pack(side="left", padx=14)

        # Atajos de teclado
        shortcuts = [
            ("F1", "Buscar"),
            ("F2", "Cobrar"),
            ("F3", "Limpiar"),
            ("F5", "Existencias"),
            ("ESC", "Cancelar"),
        ]
        for key, label in shortcuts:
            frm = tk.Frame(bar, bg=C["green"])
            frm.pack(side="right", padx=6)
            tk.Label(frm, text=key, font=font(8, "bold"), bg="#1A4D34",
                     fg=C["green_light"], padx=5, pady=1).pack(side="left")
            tk.Label(frm, text=label, font=font(9), bg=C["green"],
                     fg=C["green_bg"]).pack(side="left", padx=3)

    def _build_body(self):
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=0, pady=0)

        # Panel izquierdo: busqueda + lista de productos
        left = tk.Frame(body, bg=C["bg"], width=720)
        left.pack(side="left", fill="both", expand=True)
        left.pack_propagate(False)

        # Panel derecho: carrito
        right = tk.Frame(body, bg=C["surface"], width=400)
        right.pack(side="right", fill="both")
        right.pack_propagate(False)

        # Linea separadora
        sep = tk.Frame(body, bg=C["border"], width=1)
        sep.pack(side="right", fill="y")

        self._build_search_panel(left)
        self._build_product_list(left)
        self._build_cart(right)

    # ── PANEL BUSQUEDA ────────────────────────────────────────────
    def _build_search_panel(self, parent):
        panel = tk.Frame(parent, bg=C["surface"], bd=0)
        panel.pack(fill="x", padx=0, pady=0)

        inner = tk.Frame(panel, bg=C["surface"])
        inner.pack(fill="x", padx=18, pady=14)

        # Etiqueta
        tk.Label(inner, text="BUSCAR ARTICULO", font=font(9, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w", pady=(0, 6))

        # Fila busqueda
        row = tk.Frame(inner, bg=C["surface"])
        row.pack(fill="x")

        # Campo codigo de barras
        lbl_cod = tk.Label(row, text="Codigo / Descripcion", font=font(9),
                           bg=C["surface"], fg=C["text2"])
        lbl_cod.pack(side="left", padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search_change)

        self.entry_search = tk.Entry(
            row,
            textvariable=self.search_var,
            font=font(13),
            bg=C["surface"],
            fg=C["text"],
            insertbackground=C["green"],
            relief="solid",
            bd=1,
            highlightthickness=2,
            highlightcolor=C["green_mid"],
            highlightbackground=C["border"],
            width=30
        )
        self.entry_search.pack(side="left", ipady=6, padx=(0, 10))
        self.entry_search.bind("<Return>", self._on_search_enter)
        self.entry_search.bind("<FocusIn>", lambda e: self.entry_search.config(highlightbackground=C["green_mid"]))
        self.entry_search.bind("<FocusOut>", lambda e: self.entry_search.config(highlightbackground=C["border"]))

        btn_search = self._flat_button(
            row, "Buscar", self._do_search,
            bg=C["green"], fg="white", font_size=10
        )
        btn_search.pack(side="left", ipady=6, ipadx=12)

        # Separador inferior
        sep = tk.Frame(panel, bg=C["border"], height=1)
        sep.pack(fill="x")

    # ── LISTA DE PRODUCTOS ────────────────────────────────────────
    def _build_product_list(self, parent):
        container = tk.Frame(parent, bg=C["bg"])
        container.pack(fill="both", expand=True)

        # Cabecera tabla
        header_frame = tk.Frame(container, bg=C["green"], height=32)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        cols = [
            ("Descripcion",       1,    "w"),
            ("Codigo",            0,    "center"),
            ("Precio",            0,    "e"),
            ("Existencia",        0,    "center"),
            ("Categoria",         0,    "center"),
        ]

        col_widths = [0, 110, 80, 80, 100]

        for i, (text, _, anchor) in enumerate(cols):
            w = col_widths[i] if col_widths[i] else None
            cfg = dict(text=text, font=font(9, "bold"),
                       bg=C["green"], fg=C["green_bg"],
                       padx=8, anchor=anchor)
            if w:
                lbl = tk.Label(header_frame, width=w//7, **cfg)
            else:
                lbl = tk.Label(header_frame, **cfg)
                lbl.pack(side="left", fill="x", expand=True)
                continue
            lbl.pack(side="left")

        # Frame con scrollbar
        list_frame = tk.Frame(container, bg=C["bg"])
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                 bg=C["border"], troughcolor=C["bg"],
                                 activebackground=C["green_mid"])
        scrollbar.pack(side="right", fill="y")

        self.product_canvas = tk.Canvas(
            list_frame, bg=C["bg"],
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.product_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.product_canvas.yview)

        self.product_inner = tk.Frame(self.product_canvas, bg=C["bg"])
        self.canvas_window = self.product_canvas.create_window(
            (0, 0), window=self.product_inner, anchor="nw"
        )

        self.product_inner.bind("<Configure>", self._on_product_frame_configure)
        self.product_canvas.bind("<Configure>", self._on_product_canvas_configure)
        self.product_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.selected_product = None
        self._render_products(self.products)

        # Barra de seleccion inferior (como NOVACAJA)
        self.lbl_selected = tk.Label(
            container,
            text="",
            font=font(11, "bold"),
            bg=C["green_bg"], fg=C["green"],
            anchor="w", padx=12, pady=8
        )
        self.lbl_selected.pack(fill="x")

    def _render_products(self, products):
        for widget in self.product_inner.winfo_children():
            widget.destroy()

        self.product_rows = []

        for i, p in enumerate(products):
            bg = C["row_even"] if i % 2 == 0 else C["row_odd"]
            row = tk.Frame(self.product_inner, bg=bg, cursor="hand2")
            row.pack(fill="x")

            # Borde inferior
            sep = tk.Frame(row, bg=C["border"], height=1)

            def make_click(prod, r, orig_bg):
                def on_click(event=None):
                    self._select_product(prod, r, orig_bg)
                return on_click

            click_fn = make_click(p, row, bg)

            # Nombre (expandible)
            lbl_name = tk.Label(row, text=p["name"], font=font(11),
                                bg=bg, fg=C["text"], anchor="w",
                                padx=10, pady=8)
            lbl_name.pack(side="left", fill="x", expand=True)
            lbl_name.bind("<Button-1>", click_fn)
            lbl_name.bind("<Double-Button-1>", lambda e, prod=p: self._add_to_cart(prod))

            # Codigo
            lbl_cod = tk.Label(row, text=p["barcode"], font=mono(9),
                               bg=bg, fg=C["text2"], width=13, anchor="center",
                               padx=4, pady=8)
            lbl_cod.pack(side="left")
            lbl_cod.bind("<Button-1>", click_fn)

            # Precio
            lbl_price = tk.Label(row, text=f"${p['price']:,.2f}",
                                 font=mono(11, "bold"),
                                 bg=bg, fg=C["green"], width=9, anchor="e",
                                 padx=8, pady=8)
            lbl_price.pack(side="left")
            lbl_price.bind("<Button-1>", click_fn)

            # Existencia
            stock_color = C["red"] if p["stock"] <= 0 else (C["amber"] if p["stock"] <= 5 else C["text2"])
            lbl_stock = tk.Label(row, text=str(p["stock"]),
                                 font=mono(10),
                                 bg=bg, fg=stock_color, width=9, anchor="center",
                                 padx=4, pady=8)
            lbl_stock.pack(side="left")
            lbl_stock.bind("<Button-1>", click_fn)

            # Categoria
            lbl_cat = tk.Label(row, text=p["category"], font=font(9),
                               bg=bg, fg=C["text2"], width=13, anchor="center",
                               padx=4, pady=8)
            lbl_cat.pack(side="left")
            lbl_cat.bind("<Button-1>", click_fn)

            row.bind("<Double-Button-1>", lambda e, prod=p: self._add_to_cart(prod))

            self.product_rows.append((row, bg))

    def _select_product(self, product, row_frame, orig_bg):
        # Desmarcar anterior
        for r, bg in self.product_rows:
            for child in r.winfo_children():
                child.configure(bg=bg)
            r.configure(bg=bg)

        # Marcar actual
        row_frame.configure(bg=C["row_sel"])
        for child in row_frame.winfo_children():
            child.configure(bg=C["row_sel"], fg=C["row_sel_txt"])
            if isinstance(child, tk.Label):
                if "price" in str(child.cget("text")):
                    child.configure(fg=C["green"])

        self.selected_product = product
        self.lbl_selected.config(
            text=f"  {product['name']}   |   ${product['price']:,.2f}   |   "
                 f"Existencia: {product['stock']} {product['unit']}   |   "
                 f"Cod: {product['barcode']}"
        )

    def _on_search_change(self, *args):
        q = self.search_var.get().lower()
        if not q:
            filtered = self.products
        else:
            filtered = [
                p for p in self.products
                if q in p["name"].lower() or q in p["barcode"]
            ]
        self._render_products(filtered)

    def _on_search_enter(self, event):
        # Si hay exactamente un resultado, agregarlo al carrito
        q = self.search_var.get().strip()
        if not q:
            return

        # Buscar por codigo de barras exacto
        match = next((p for p in self.products if p["barcode"] == q), None)
        if match:
            self._add_to_cart(match)
            self.search_var.set("")
            return

        # Un solo resultado
        filtered = [p for p in self.products if q.lower() in p["name"].lower()]
        if len(filtered) == 1:
            self._add_to_cart(filtered[0])
            self.search_var.set("")

    def _do_search(self):
        self.entry_search.focus()

    # ── CARRITO ───────────────────────────────────────────────────
    def _build_cart(self, parent):
        # Titulo
        title_frame = tk.Frame(parent, bg=C["surface"])
        title_frame.pack(fill="x", padx=0)

        inner_title = tk.Frame(title_frame, bg=C["surface"])
        inner_title.pack(fill="x", padx=16, pady=12)

        tk.Label(inner_title, text="VENTA ACTUAL", font=font(10, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")

        btn_clear = self._flat_button(
            inner_title, "Limpiar todo", self._clear_cart,
            bg=C["red_bg"], fg=C["red"], font_size=9
        )
        btn_clear.pack(side="right", ipadx=8, ipady=3)

        # Separador
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x")

        # Header columnas carrito
        hdr = tk.Frame(parent, bg=C["bg"])
        hdr.pack(fill="x")
        tk.Label(hdr, text="Articulo", font=font(9, "bold"),
                 bg=C["bg"], fg=C["text2"], anchor="w",
                 padx=12, pady=6).pack(side="left", fill="x", expand=True)
        tk.Label(hdr, text="Cant", font=font(9, "bold"),
                 bg=C["bg"], fg=C["text2"], anchor="center",
                 padx=4, pady=6, width=5).pack(side="left")
        tk.Label(hdr, text="Subtotal", font=font(9, "bold"),
                 bg=C["bg"], fg=C["text2"], anchor="e",
                 padx=12, pady=6, width=9).pack(side="left")

        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x")

        # Lista carrito con scroll
        cart_frame = tk.Frame(parent, bg=C["surface"])
        cart_frame.pack(fill="both", expand=True)

        cart_scroll = tk.Scrollbar(cart_frame, orient="vertical")
        cart_scroll.pack(side="right", fill="y")

        self.cart_canvas = tk.Canvas(
            cart_frame, bg=C["surface"],
            yscrollcommand=cart_scroll.set,
            highlightthickness=0
        )
        self.cart_canvas.pack(side="left", fill="both", expand=True)
        cart_scroll.config(command=self.cart_canvas.yview)

        self.cart_inner = tk.Frame(self.cart_canvas, bg=C["surface"])
        self.cart_canvas_win = self.cart_canvas.create_window(
            (0, 0), window=self.cart_inner, anchor="nw"
        )

        self.cart_inner.bind("<Configure>", lambda e: self.cart_canvas.configure(
            scrollregion=self.cart_canvas.bbox("all")
        ))
        self.cart_canvas.bind("<Configure>", lambda e: self.cart_canvas.itemconfig(
            self.cart_canvas_win, width=e.width
        ))

        # ── TOTALES ───────────────────────────────────────────────
        totals = tk.Frame(parent, bg=C["surface"])
        totals.pack(fill="x", side="bottom")

        tk.Frame(totals, bg=C["border"], height=1).pack(fill="x")

        totals_inner = tk.Frame(totals, bg=C["surface"])
        totals_inner.pack(fill="x", padx=16, pady=10)

        # Conteo items
        row_items = tk.Frame(totals_inner, bg=C["surface"])
        row_items.pack(fill="x", pady=2)
        tk.Label(row_items, text="Articulos:", font=font(10),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")
        self.lbl_items_count = tk.Label(row_items, text="0", font=mono(10, "bold"),
                                         bg=C["surface"], fg=C["text"])
        self.lbl_items_count.pack(side="right")

        # Total
        row_total = tk.Frame(totals_inner, bg=C["surface"])
        row_total.pack(fill="x", pady=4)
        tk.Label(row_total, text="TOTAL:", font=font(14, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(side="left")
        self.lbl_total = tk.Label(row_total, text="$0.00", font=mono(18, "bold"),
                                   bg=C["surface"], fg=C["green"])
        self.lbl_total.pack(side="right")

        tk.Frame(totals, bg=C["border"], height=1).pack(fill="x")

        # ── METODO DE PAGO ────────────────────────────────────────
        pay_frame = tk.Frame(totals, bg=C["surface"])
        pay_frame.pack(fill="x", padx=16, pady=8)

        tk.Label(pay_frame, text="METODO DE PAGO", font=font(9, "bold"),
                 bg=C["surface"], fg=C["text2"]).pack(anchor="w", pady=(0, 6))

        btns_pay = tk.Frame(pay_frame, bg=C["surface"])
        btns_pay.pack(fill="x")

        self.pay_var = tk.StringVar(value="efectivo")
        pay_opts = [("Efectivo", "efectivo"), ("Tarjeta", "tarjeta"), ("Transf.", "transferencia")]
        self.pay_buttons = {}
        for label, val in pay_opts:
            btn = tk.Radiobutton(
                btns_pay, text=label, value=val, variable=self.pay_var,
                font=font(10), bg=C["green_bg"], fg=C["green"],
                selectcolor=C["green"], activebackground=C["green_bg"],
                indicatoron=False,
                relief="flat", bd=0,
                padx=10, pady=6,
                cursor="hand2",
                command=self._on_payment_change
            )
            btn.pack(side="left", fill="x", expand=True, padx=2)
            self.pay_buttons[val] = btn

        self._update_pay_buttons()

        # Campo efectivo recibido
        self.efectivo_frame = tk.Frame(totals, bg=C["surface"])
        self.efectivo_frame.pack(fill="x", padx=16, pady=(0, 6))

        ef_row = tk.Frame(self.efectivo_frame, bg=C["surface"])
        ef_row.pack(fill="x")
        tk.Label(ef_row, text="Recibido:", font=font(10),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")

        self.efectivo_var = tk.StringVar()
        self.efectivo_var.trace_add("write", self._calc_cambio)
        self.entry_efectivo = tk.Entry(
            ef_row,
            textvariable=self.efectivo_var,
            font=mono(13, "bold"),
            width=10,
            justify="right",
            bg=C["bg"], fg=C["text"],
            insertbackground=C["green"],
            relief="solid", bd=1,
            highlightthickness=1,
            highlightcolor=C["green_mid"],
            highlightbackground=C["border"]
        )
        self.entry_efectivo.pack(side="right", ipady=5)

        # Cambio
        cambio_row = tk.Frame(self.efectivo_frame, bg=C["surface"])
        cambio_row.pack(fill="x", pady=(4, 0))
        tk.Label(cambio_row, text="Cambio:", font=font(10),
                 bg=C["surface"], fg=C["text2"]).pack(side="left")
        self.lbl_cambio = tk.Label(cambio_row, text="$0.00",
                                    font=mono(13, "bold"),
                                    bg=C["surface"], fg=C["amber"])
        self.lbl_cambio.pack(side="right")

        # ── BOTON COBRAR ──────────────────────────────────────────
        btn_area = tk.Frame(totals, bg=C["surface"])
        btn_area.pack(fill="x", padx=16, pady=(4, 16))

        self.btn_cobrar = tk.Button(
            btn_area,
            text="COBRAR   F2",
            font=font(14, "bold"),
            bg=C["green"],
            fg="white",
            activebackground=C["green_mid"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            command=self._process_sale
        )
        self.btn_cobrar.pack(fill="x", ipady=14)

        # Bind F2
        self.bind_all("<F2>", lambda e: self._process_sale())
        self.bind_all("<F1>", lambda e: self.entry_search.focus_set())
        self.bind_all("<F3>", lambda e: self._clear_cart())
        self.bind_all("<Escape>", lambda e: self._clear_selection())

    def _on_payment_change(self):
        self._update_pay_buttons()
        if self.pay_var.get() == "efectivo":
            self.efectivo_frame.pack(fill="x", padx=16, pady=(0, 6))
        else:
            self.efectivo_frame.pack_forget()

    def _update_pay_buttons(self):
        for val, btn in self.pay_buttons.items():
            if val == self.pay_var.get():
                btn.config(bg=C["green"], fg="white", font=font(10, "bold"))
            else:
                btn.config(bg=C["green_bg"], fg=C["green"], font=font(10))

    def _render_cart(self):
        for w in self.cart_inner.winfo_children():
            w.destroy()

        if not self.cart:
            tk.Label(self.cart_inner, text="Sin articulos",
                     font=font(11), bg=C["surface"], fg=C["text3"],
                     pady=30).pack()
            return

        for i, item in enumerate(self.cart):
            bg = C["row_even"] if i % 2 == 0 else C["row_odd"]
            row = tk.Frame(self.cart_inner, bg=bg)
            row.pack(fill="x")

            # Nombre + precio unitario
            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            tk.Label(info, text=item["product"]["name"],
                     font=font(10, "bold"), bg=bg, fg=C["text"],
                     anchor="w", wraplength=180, justify="left").pack(anchor="w")
            tk.Label(info, text=f"${item['product']['price']:,.2f} c/u",
                     font=mono(9), bg=bg, fg=C["text2"]).pack(anchor="w")

            # Controles cantidad
            ctrl = tk.Frame(row, bg=bg)
            ctrl.pack(side="left", pady=8)

            tk.Button(ctrl, text="-", font=font(11, "bold"),
                      bg=C["border"], fg=C["text"],
                      relief="flat", bd=0, width=2, cursor="hand2",
                      command=lambda idx=i: self._change_qty(idx, -1)
                      ).pack(side="left")

            tk.Label(ctrl, text=str(item["qty"]),
                     font=mono(11, "bold"), bg=bg, fg=C["text"],
                     width=3, anchor="center").pack(side="left")

            tk.Button(ctrl, text="+", font=font(11, "bold"),
                      bg=C["border"], fg=C["text"],
                      relief="flat", bd=0, width=2, cursor="hand2",
                      command=lambda idx=i: self._change_qty(idx, 1)
                      ).pack(side="left")

            # Subtotal
            tk.Label(row, text=f"${item['subtotal']:,.2f}",
                     font=mono(11, "bold"), bg=bg, fg=C["green"],
                     width=9, anchor="e", padx=10, pady=8
                     ).pack(side="left")

            # Borrar item
            tk.Button(row, text="x", font=font(9),
                      bg=bg, fg=C["text3"],
                      relief="flat", bd=0, cursor="hand2",
                      command=lambda idx=i: self._remove_item(idx)
                      ).pack(side="left", padx=(0, 6))

            tk.Frame(self.cart_inner, bg=C["border"], height=1).pack(fill="x")

        self.cart_canvas.update_idletasks()
        self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all"))

    def _update_totals(self):
        total = sum(i["subtotal"] for i in self.cart)
        count = sum(i["qty"] for i in self.cart)
        self.lbl_total.config(text=f"${total:,.2f}")
        self.lbl_items_count.config(text=str(count))
        self.btn_cobrar.config(
            text=f"COBRAR  ${total:,.2f}   F2",
            state="normal" if self.cart else "disabled",
            bg=C["green"] if self.cart else C["text3"]
        )
        self._calc_cambio()

    def _calc_cambio(self, *args):
        try:
            recibido = float(self.efectivo_var.get() or 0)
        except ValueError:
            recibido = 0
        total = sum(i["subtotal"] for i in self.cart)
        cambio = max(0, recibido - total)
        self.lbl_cambio.config(
            text=f"${cambio:,.2f}",
            fg=C["green"] if cambio > 0 else C["amber"]
        )

    def _add_to_cart(self, product):
        if product["stock"] <= 0:
            messagebox.showwarning("Sin existencia",
                                   f"'{product['name']}' no tiene existencia disponible.")
            return

        existing = next((i for i in self.cart if i["product"]["id"] == product["id"]), None)
        if existing:
            if existing["qty"] >= product["stock"]:
                messagebox.showwarning("Limite de stock",
                                       f"Solo hay {product['stock']} unidades disponibles.")
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
        self.entry_search.focus_set()

    def _change_qty(self, idx, delta):
        item = self.cart[idx]
        new_qty = item["qty"] + delta
        if new_qty <= 0:
            self._remove_item(idx)
            return
        if new_qty > item["product"]["stock"]:
            messagebox.showwarning("Limite",
                                   f"Solo hay {item['product']['stock']} unidades.")
            return
        item["qty"] = new_qty
        item["subtotal"] = new_qty * item["product"]["price"]
        self._render_cart()
        self._update_totals()

    def _remove_item(self, idx):
        self.cart.pop(idx)
        self._render_cart()
        self._update_totals()

    def _clear_cart(self):
        if not self.cart:
            return
        if messagebox.askyesno("Limpiar venta",
                                "¿Cancelar todos los articulos de la venta actual?"):
            self.cart.clear()
            self._render_cart()
            self._update_totals()

    def _clear_selection(self):
        self.search_var.set("")
        self.entry_search.focus_set()

    # ── PROCESAR VENTA ────────────────────────────────────────────
    def _process_sale(self):
        if not self.cart:
            return

        total = sum(i["subtotal"] for i in self.cart)
        metodo = self.pay_var.get()

        if metodo == "efectivo":
            try:
                recibido = float(self.efectivo_var.get() or 0)
            except ValueError:
                recibido = 0
            if recibido < total:
                messagebox.showwarning("Efectivo insuficiente",
                                       f"El monto recibido (${recibido:,.2f}) es menor al total (${total:,.2f}).")
                self.entry_efectivo.focus_set()
                return
            cambio = recibido - total
        else:
            recibido = total
            cambio = 0

        folio = f"F{self.folio_counter:04d}"
        self.folio_counter += 1

        # Descuento de inventario mock
        for item in self.cart:
            for p in self.products:
                if p["id"] == item["product"]["id"]:
                    p["stock"] -= item["qty"]

        # Mostrar dialogo de exito
        self._show_success_dialog(folio, total, metodo, recibido, cambio)

        self.cart.clear()
        self.efectivo_var.set("")
        self._render_cart()
        self._update_totals()
        self._render_products(self.products)
        self.entry_search.focus_set()

    def _show_success_dialog(self, folio, total, metodo, recibido, cambio):
        dlg = tk.Toplevel(self)
        dlg.title("Venta Completada")
        dlg.configure(bg=C["surface"])
        dlg.resizable(False, False)
        dlg.grab_set()

        w, h = 360, 380
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        dlg.geometry(f"{w}x{h}+{x}+{y}")

        # Banda superior verde
        top = tk.Frame(dlg, bg=C["green"], height=8)
        top.pack(fill="x")

        inner = tk.Frame(dlg, bg=C["surface"])
        inner.pack(fill="both", expand=True, padx=30, pady=24)

        tk.Label(inner, text="Venta Registrada", font=font(16, "bold"),
                 bg=C["surface"], fg=C["text"]).pack(pady=(0, 4))
        tk.Label(inner, text=datetime.now().strftime("%d/%m/%Y  %H:%M:%S"),
                 font=mono(10), bg=C["surface"], fg=C["text2"]).pack()

        tk.Frame(inner, bg=C["border"], height=1).pack(fill="x", pady=16)

        def info_row(label, value, value_color=C["text"]):
            r = tk.Frame(inner, bg=C["surface"])
            r.pack(fill="x", pady=3)
            tk.Label(r, text=label, font=font(10), bg=C["surface"], fg=C["text2"]).pack(side="left")
            tk.Label(r, text=value, font=mono(11, "bold"), bg=C["surface"], fg=value_color).pack(side="right")

        info_row("Folio:", folio)
        info_row("Total:", f"${total:,.2f}", C["green"])
        info_row("Metodo:", metodo.capitalize())
        if metodo == "efectivo":
            info_row("Recibido:", f"${recibido:,.2f}")
            info_row("Cambio:", f"${cambio:,.2f}", C["amber"])

        tk.Frame(inner, bg=C["border"], height=1).pack(fill="x", pady=16)

        tk.Label(inner, text=f"Cajero: {self.user['name']}",
                 font=font(9), bg=C["surface"], fg=C["text2"]).pack()

        btn = tk.Button(
            inner, text="Nueva Venta",
            font=font(12, "bold"),
            bg=C["green"], fg="white",
            activebackground=C["green_mid"], activeforeground="white",
            relief="flat", bd=0, cursor="hand2",
            command=dlg.destroy
        )
        btn.pack(fill="x", ipady=10, pady=(16, 0))

        dlg.bind("<Return>", lambda e: dlg.destroy())
        dlg.bind("<Escape>", lambda e: dlg.destroy())
        btn.focus_set()

    # ── UTILIDADES ────────────────────────────────────────────────
    def _flat_button(self, parent, text, command, bg, fg, font_size=10):
        return tk.Button(
            parent, text=text, command=command,
            font=font(font_size),
            bg=bg, fg=fg,
            activebackground=bg, activeforeground=fg,
            relief="flat", bd=0, cursor="hand2"
        )

    def _start_clock(self):
        def tick():
            while True:
                now = datetime.now().strftime("%H:%M:%S  %d/%m/%Y")
                try:
                    self.lbl_clock.config(text=now)
                except Exception:
                    break
                time.sleep(1)
        t = threading.Thread(target=tick, daemon=True)
        t.start()

    def _on_product_frame_configure(self, event):
        self.product_canvas.configure(
            scrollregion=self.product_canvas.bbox("all")
        )

    def _on_product_canvas_configure(self, event):
        self.product_canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        widget = event.widget
        # Solo scroll si el mouse esta sobre la lista de productos
        try:
            self.product_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════
#  ENTRADA
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = CajaApp()
    app.mainloop()
