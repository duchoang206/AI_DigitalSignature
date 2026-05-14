# main_app.py — AI-ECDSA với giao diện Microsoft Surface City style

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.core.elliptic_curve import EllipticCurve, get_available_curves
from src.core.ecdsa import ECDSA, ECGDSA
from src.core.ec_elgamal import ECElGamal
from src.ai.ip_guardian import IPGuardian

# ══════════════════════════════════════════════════════════════════
#  DESIGN TOKENS  — Microsoft Surface City palette
# ══════════════════════════════════════════════════════════════════
MS_BLUE      = "#0067B8"   # xanh Microsoft chính
MS_BLUE_DK   = "#005a9e"   # hover xanh
MS_RED       = "#E30E18"   # đỏ giá / sale
MS_GOLD      = "#FFB900"   # vàng Microsoft
WHITE        = "#FFFFFF"
GRAY_BG      = "#F4F4F4"   # nền tổng thể
GRAY_PANEL   = "#FAFAFA"   # nền panel trắng nhạt
GRAY_BORDER  = "#E0E0E0"   # đường kẻ
GRAY_TEXT    = "#333333"   # văn bản chính
GRAY_MUTED   = "#777777"   # văn bản phụ
ENTRY_BG     = "#FFFFFF"
SUCCESS_GR   = "#107C10"   # xanh lá Microsoft
WARN_OR      = "#D83B01"   # cam cảnh báo

FONT_LOGO    = ("Segoe UI", 13, "bold")
FONT_SUBBRAND= ("Segoe UI", 8)
FONT_NAV     = ("Segoe UI", 10)
FONT_TITLE   = ("Segoe UI Semibold", 12)
FONT_LABEL   = ("Segoe UI", 9)
FONT_BODY    = ("Segoe UI", 10)
FONT_MONO    = ("Consolas", 9)
FONT_MONO_SM = ("Consolas", 8)
FONT_BTN     = ("Segoe UI Semibold", 9)


def _btn(parent, text, cmd, bg=MS_BLUE, fg=WHITE, pad_x=14, pad_y=6):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=fg, activebackground=MS_BLUE_DK,
                  activeforeground=WHITE, relief="flat",
                  cursor="hand2", font=FONT_BTN,
                  padx=pad_x, pady=pad_y, bd=0)
    b.bind("<Enter>", lambda e: b.config(bg=MS_BLUE_DK if bg == MS_BLUE else bg))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b


def _entry_txt(parent, h=4, w=55):
    t = scrolledtext.ScrolledText(
        parent, height=h, width=w,
        bg=ENTRY_BG, fg=GRAY_TEXT, insertbackground=GRAY_TEXT,
        relief="solid", bd=1, font=FONT_MONO, wrap=tk.WORD,
        highlightthickness=1, highlightbackground=GRAY_BORDER,
        highlightcolor=MS_BLUE
    )
    return t


def _sep(parent, color=GRAY_BORDER, h=1):
    tk.Frame(parent, bg=color, height=h).pack(fill="x")


# ══════════════════════════════════════════════════════════════════
#  LOGO MICROSOFT  (4 ô màu vẽ bằng Canvas)
# ══════════════════════════════════════════════════════════════════
def _ms_logo(parent, size=16):
    c = tk.Canvas(parent, width=size, height=size,
                  bg=parent.cget("bg"), highlightthickness=0)
    half = size // 2
    gap  = max(1, size // 16)
    c.create_rectangle(0,    0,    half-gap, half-gap, fill="#F25022", outline="")
    c.create_rectangle(half, 0,    size,     half-gap, fill="#7FBA00", outline="")
    c.create_rectangle(0,    half, half-gap, size,     fill="#00A4EF", outline="")
    c.create_rectangle(half, half, size,     size,     fill="#FFB900", outline="")
    return c


# ══════════════════════════════════════════════════════════════════
#  APP
# ══════════════════════════════════════════════════════════════════
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-ECDSA | Microsoft Surface City")
        self.configure(bg=GRAY_BG)
        self.geometry("1280x850")
        self.minsize(1100, 700)
        self.resizable(True, True)

        self.guardian = IPGuardian()

        # self._build_topbar() # Ẩn topbar
        self._build_header()
        self._build_navbar()
        self._build_body()
        self._build_floating_buttons()
        self._build_statusbar()

    # ══════════════════════════════════════════════════
    #  TOP BAR — xanh nhạt, hotline + link
    # ══════════════════════════════════════════════════
    def _build_topbar(self):
        bar = tk.Frame(self, bg="#EEF4FB", height=26)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="Hotline: ", bg="#EEF4FB",
                 fg=GRAY_MUTED, font=("Segoe UI", 8)).pack(side="left", padx=(12, 0))
        tk.Label(bar, text="0936.287.733", bg="#EEF4FB",
                 fg=MS_RED, font=("Segoe UI Semibold", 8)).pack(side="left")
        
        for lbl in ["Trang chủ", "Giới thiệu", "Liên hệ"]:
            tk.Label(bar, text=lbl, bg="#EEF4FB", fg=MS_BLUE,
                     font=("Segoe UI", 8), cursor="hand2").pack(side="right", padx=10)

    # ══════════════════════════════════════════════════
    #  HEADER — logo + search bar
    # ══════════════════════════════════════════════════
    def _build_header(self):
        hdr = tk.Frame(self, bg=MS_BLUE, height=70)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        inner = tk.Frame(hdr, bg=MS_BLUE)
        inner.pack(fill="both", expand=True, padx=40)

        # ── Logo ──────────────────────────────────────
        logo_frame = tk.Frame(inner, bg=MS_BLUE)
        logo_frame.pack(side="left", pady=15)

        ms_logo = _ms_logo(logo_frame, size=24)
        ms_logo.config(bg=MS_BLUE)
        ms_logo.pack(side="left", padx=(0, 6))

        txt_wrap = tk.Frame(logo_frame, bg=MS_BLUE)
        txt_wrap.pack(side="left")
        tk.Label(txt_wrap, text="Microsoft", bg=MS_BLUE,
                 fg=WHITE, font=("Segoe UI", 9)).pack(anchor="w", pady=(0,0))
        tk.Label(txt_wrap, text="Surfacecity", bg=MS_BLUE,
                 fg=WHITE, font=("Segoe UI Semibold", 15),
                 cursor="hand2").pack(anchor="w", pady=(0,0))

        # ── Search Bar ─────────────────────────────────
        search_wrap = tk.Frame(inner, bg=MS_BLUE)
        search_wrap.pack(side="left", fill="both", expand=True, padx=60, pady=16)
        
        search_bg = tk.Frame(search_wrap, bg=WHITE)
        search_bg.pack(fill="both", expand=True)
        
        search_entry = tk.Entry(search_bg, bg=WHITE, fg=GRAY_TEXT, font=("Segoe UI", 10), bd=0, insertbackground=GRAY_TEXT)
        search_entry.insert(0, "Bạn muốn mua gì hôm nay?")
        search_entry.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        tk.Label(search_bg, text="🔍", bg=WHITE, fg=GRAY_TEXT).pack(side="right", padx=10)

        # ── Right icons ───────────────────────────────
        right = tk.Frame(inner, bg=MS_BLUE)
        right.pack(side="right", pady=15)
        for icon, lbl in [("🏠", "Trang chủ"), ("🛒", "Giỏ hàng")]:
            f = tk.Frame(right, bg=MS_BLUE, cursor="hand2")
            f.pack(side="left", padx=15)
            tk.Label(f, text=icon, bg=MS_BLUE, fg=WHITE, font=("Segoe UI", 14)).pack(side="left")
            tk.Label(f, text=lbl, bg=MS_BLUE, fg=WHITE, font=("Segoe UI Semibold", 9)).pack(side="left", padx=(5,0))

    # ══════════════════════════════════════════════════
    #  NAVBAR — xanh Microsoft
    # ══════════════════════════════════════════════════
    def _build_navbar(self):
        nav = tk.Frame(self, bg=MS_BLUE, height=40)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        tabs_info = [
            ("Surface Pro", 0),
            ("Surface Laptop", 0),
            ("Surface Book", 0),
            ("Surface Go", 0),
            ("Surface Laptop Studio", 0),
            ("Surface Studio", 0),
            ("Phụ kiện", 0),
            ("Tin tức", 0),
            (" | ", None),
            ("🔏 Chữ ký số", 1),
            ("🔒 Mã hóa EC", 2),
            ("🤖 AI Guardian", 3),
        ]
        self._nav_btns = []
        inner_nav = tk.Frame(nav, bg=MS_BLUE)
        inner_nav.pack(anchor="center", fill="y")
        
        for text, idx in tabs_info:
            b = tk.Label(inner_nav, text=text, bg=MS_BLUE, fg=WHITE,
                         font=("Segoe UI Semibold", 9),
                         padx=12, pady=10, cursor="hand2" if idx is not None else "")
            b.pack(side="left")
            if idx is not None:
                b.bind("<Button-1>", lambda e, i=idx: self._nb.select(i))
                b.bind("<Enter>", lambda e, w=b: w.config(bg="#005090"))
                b.bind("<Leave>", lambda e, w=b, i=idx: w.config(
                    bg="#003d7a" if self._nb.index("current") == i else MS_BLUE))
            self._nav_btns.append((b, idx))

    # ══════════════════════════════════════════════════
    #  BODY — Notebook 4 tab
    # ══════════════════════════════════════════════════
    def _build_body(self):
        body = tk.Frame(self, bg=WHITE)
        body.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("SC.TNotebook", background=WHITE, borderwidth=0)
        style.layout("SC.TNotebook.Tab", []) # Ẩn tab mặc định

        self._nb = ttk.Notebook(body, style="SC.TNotebook")
        self._nb.pack(fill="both", expand=True)

        self.tab_home  = tk.Frame(self._nb, bg=WHITE)
        
        self.tab_sig_outer = tk.Frame(self._nb, bg=GRAY_BG)
        self.tab_sig = tk.Frame(self.tab_sig_outer, bg=GRAY_BG)
        self.tab_sig.pack(fill="both", expand=True, padx=14, pady=10)
        
        self.tab_enc_outer = tk.Frame(self._nb, bg=GRAY_BG)
        self.tab_enc = tk.Frame(self.tab_enc_outer, bg=GRAY_BG)
        self.tab_enc.pack(fill="both", expand=True, padx=14, pady=10)
        
        self.tab_guard_outer = tk.Frame(self._nb, bg=GRAY_BG)
        self.tab_guard = tk.Frame(self.tab_guard_outer, bg=GRAY_BG)
        self.tab_guard.pack(fill="both", expand=True, padx=14, pady=10)

        self._nb.add(self.tab_home,  text="Home")
        self._nb.add(self.tab_sig_outer,   text="Sig")
        self._nb.add(self.tab_enc_outer,   text="Enc")
        self._nb.add(self.tab_guard_outer, text="Guard")

        self._build_tab_home(self.tab_home)
        self._build_tab_sig(self.tab_sig)
        self._build_tab_enc(self.tab_enc)
        self._build_tab_guard(self.tab_guard)

        self._nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        
    def _on_tab_changed(self, event):
        current = self._nb.index("current")
        for btn, idx in self._nav_btns:
            if idx is not None:
                btn.config(bg="#003d7a" if idx == current else MS_BLUE)

    def _build_tab_home(self, parent):
        container = tk.Frame(parent, bg=WHITE)
        container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # TOP ROW: Banner + News
        top_row = tk.Frame(container, bg=WHITE)
        top_row.pack(fill="x", pady=(0, 20))
        
        # Banner (Left)
        banner = tk.Frame(top_row, bg="#D11928", height=320)
        banner.pack(side="left", fill="both", expand=True, padx=(0, 20))
        banner.pack_propagate(False)
        tk.Label(banner, text="HÀO KHÍ", bg="#D11928", fg="#FFD700", font=("Segoe UI Black", 32)).pack(pady=(60, 0))
        tk.Label(banner, text="NGẤT TRỜI", bg="#D11928", fg=WHITE, font=("Segoe UI Black", 48)).pack()
        tk.Label(banner, text="SURFACECITY GIẢM HỜI CỰC CHẤT", bg="#D11928", fg=WHITE, font=("Segoe UI Semibold", 16)).pack(pady=(10, 0))
        
        # News (Right)
        news_frame = tk.Frame(top_row, bg=WHITE, width=350, highlightthickness=1, highlightbackground=GRAY_BORDER)
        news_frame.pack(side="right", fill="y")
        news_frame.pack_propagate(False)
        
        n_hdr = tk.Frame(news_frame, bg="#F8F9FA")
        n_hdr.pack(fill="x")
        tk.Label(n_hdr, text="📰 TIN SURFACE", bg="#F8F9FA", fg=MS_BLUE, font=("Segoe UI", 11, "bold"), pady=10, padx=10).pack(anchor="w")
        
        news_items = [
            "SurfaceCity mở bán sạc và pin dự phòng Anker chính hãng, giá tốt",
            "Surface Pro 12 inch và MacBook Neo: đâu là lựa chọn phù hợp hơn?",
            "So sánh Surface Laptop 13 inch và MacBook Neo: Mức giá quá cao?",
            "Surface Pro 12 và Surface Laptop 8: Rò rỉ cấu hình mạnh mẽ, kỷ nguyên AI"
        ]
        for item in news_items:
            f = tk.Frame(news_frame, bg=WHITE)
            f.pack(fill="x", padx=10, pady=10)
            tk.Label(f, text="◾", bg=WHITE, fg=MS_BLUE, font=("Segoe UI", 10)).pack(side="left", anchor="n", padx=(0, 5))
            tk.Label(f, text=item, bg=WHITE, fg=GRAY_TEXT, font=("Segoe UI", 9), wraplength=300, justify="left", cursor="hand2").pack(side="left", anchor="n")
        
        # BOTTOM ROW: Flash Sale
        sale_frame = tk.Frame(container, bg=WHITE, highlightthickness=1, highlightbackground="#E30E18")
        sale_frame.pack(fill="x")
        
        s_hdr = tk.Frame(sale_frame, bg=WHITE)
        s_hdr.pack(fill="x", padx=15, pady=10)
        tk.Label(s_hdr, text="🎁 SURFACECITY: MICROSOFT SURFACE CHÍNH HÃNG", bg=WHITE, fg="#E30E18", font=("Segoe UI", 14, "bold")).pack(side="left")
        
        products_frame = tk.Frame(sale_frame, bg=WHITE)
        products_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        prods = [
            ("Surface Pro 8 i5/8GB/128GB (Newseal)", "16.490.000đ"),
            ("(Combo kèm phím) Surface Pro 7 Plus i5/8GB/256GB", "17.990.000đ"),
            ("Surface Pro 11 Snapdragon X Plus/16GB/256GB", "28.990.000đ"),
            ("Surface Laptop 7 13.8 inch Snapdragon X", "29.990.000đ")
        ]
        
        for name, price in prods:
            card = tk.Frame(products_frame, bg=WHITE, highlightthickness=1, highlightbackground=GRAY_BORDER)
            card.pack(side="left", fill="both", expand=True, padx=10)
            
            img_frame = tk.Frame(card, bg=WHITE, height=140)
            img_frame.pack(fill="x", padx=10, pady=10)
            img_frame.pack_propagate(False)
            c = tk.Canvas(img_frame, bg=WHITE, highlightthickness=0)
            c.pack(fill="both", expand=True)
            c.create_oval(30, 20, 100, 90, fill="#E6F2FF", outline="")
            c.create_polygon(50, 40, 120, 40, 140, 100, 30, 100, fill="#404040", outline="")
            c.create_polygon(55, 45, 115, 45, 125, 80, 45, 80, fill="#1A73E8", outline="")
            
            tk.Label(card, text="  Trả góp 0%  ", bg="#E30E18", fg=WHITE, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10)
            tk.Label(card, text=name, bg=WHITE, fg=GRAY_TEXT, font=("Segoe UI", 9), wraplength=180, justify="left", cursor="hand2").pack(anchor="w", padx=10, pady=(8,0))
            tk.Label(card, text=price, bg=WHITE, fg="#E30E18", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=10, pady=(5,15))

    def _build_floating_buttons(self):
        fb = tk.Label(self, text="f", bg="#1877F2", fg=WHITE, font=("Segoe UI", 16, "bold"), width=2, height=1, cursor="hand2")
        fb.place(x=20, y=400)
        zl = tk.Label(self, text="Z", bg="#0068FF", fg=WHITE, font=("Segoe UI", 16, "bold"), width=2, height=1, cursor="hand2")
        zl.place(x=20, y=450)
        ph = tk.Label(self, text="📞 0936287733", bg="#0068FF", fg=WHITE, font=("Segoe UI", 10, "bold"), padx=10, pady=5, cursor="hand2")
        ph.place(x=20, y=500)
        
        msg = tk.Label(self, text="~", bg="#0084FF", fg=WHITE, font=("Segoe UI", 16, "bold"), width=2, height=1, cursor="hand2")
        msg.place(relx=1.0, x=-50, y=500)

    # ══════════════════════════════════════════════════
    #  STATUS BAR
    # ══════════════════════════════════════════════════
    def _build_statusbar(self):
        bar = tk.Frame(self, bg=MS_BLUE, height=24)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        self._status_var = tk.StringVar(value="✅  Sẵn sàng  |  AI Guardian: ONLINE")
        tk.Label(bar, textvariable=self._status_var,
                 bg=MS_BLUE, fg=WHITE, font=("Segoe UI", 8),
                 anchor="w", padx=14).pack(fill="both", expand=True)

    def _set_status(self, msg):
        self._status_var.set(f"●  {msg}")

    # ── shared helper ─────────────────────────────────
    def _run(self, fn, *a):
        threading.Thread(target=fn, args=a, daemon=True).start()

    # ══════════════════════════════════════════════════
    #  TAB 1 — Chữ ký số
    # ══════════════════════════════════════════════════
    def _build_tab_sig(self, parent):
        # ── LEFT panel ────────────────────────────────
        left = tk.Frame(parent, bg=WHITE, bd=0,
                        highlightthickness=1, highlightbackground=GRAY_BORDER)
        left.pack(side="left", fill="y", padx=(0, 8), pady=0)

        # Panel title
        ptitle = tk.Frame(left, bg=MS_BLUE)
        ptitle.pack(fill="x")
        tk.Label(ptitle, text="⚙️  Cấu hình thuật toán",
                 bg=MS_BLUE, fg=WHITE,
                 font=("Segoe UI Semibold", 10),
                 padx=12, pady=8).pack(anchor="w")

        body = tk.Frame(left, bg=WHITE)
        body.pack(fill="both", padx=14, pady=10)

        # Đường cong
        self._lbl(body, "Đường cong Elliptic:").grid(
            row=0, column=0, sticky="w", pady=(0, 2))
        self.sig_curve_var = tk.StringVar(value="secp112r1")
        cb = ttk.Combobox(body, textvariable=self.sig_curve_var,
                          values=get_available_curves(ecdsa_only=True),
                          width=20, state="readonly", font=FONT_LABEL)
        cb.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Thuật toán
        self._lbl(body, "Thuật toán:").grid(
            row=2, column=0, sticky="w", pady=(0, 2))
        self.sig_algo_var = tk.StringVar(value="ECDSA")
        rf = tk.Frame(body, bg=WHITE)
        rf.grid(row=3, column=0, columnspan=2, sticky="w", pady=(0, 10))
        for algo in ["ECDSA", "ECGDSA"]:
            tk.Radiobutton(rf, text=algo, variable=self.sig_algo_var,
                           value=algo, bg=WHITE, fg=GRAY_TEXT,
                           selectcolor=WHITE, activebackground=WHITE,
                           font=FONT_BODY).pack(side="left", padx=4)

        # Nút tạo khóa
        _btn(body, "🔑  Tạo cặp khóa", self._sig_gen,
             bg=MS_BLUE, pad_x=12, pad_y=7).grid(
            row=4, column=0, columnspan=2, sticky="ew", pady=(4, 12))

        tk.Frame(body, bg=GRAY_BORDER, height=1).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        # Private key
        self._lbl(body, "Khóa riêng (d):").grid(
            row=6, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.sig_priv_txt = _entry_txt(body, h=3, w=34)
        self.sig_priv_txt.grid(row=7, column=0, columnspan=2,
                                sticky="ew", pady=(0, 8))

        # Public key
        self._lbl(body, "Khóa công khai (Q):").grid(
            row=8, column=0, columnspan=2, sticky="w", pady=(0, 2))
        self.sig_pub_txt = _entry_txt(body, h=4, w=34)
        self.sig_pub_txt.grid(row=9, column=0, columnspan=2,
                               sticky="ew", pady=(0, 6))

        self.sig_time_var = tk.StringVar()
        tk.Label(body, textvariable=self.sig_time_var,
                 bg=WHITE, fg=MS_BLUE, font=("Segoe UI", 8)).grid(
            row=10, column=0, columnspan=2, sticky="w")

        # ── RIGHT panel ───────────────────────────────
        right = tk.Frame(parent, bg=GRAY_BG)
        right.pack(side="left", fill="both", expand=True)

        # Message box card
        msg_card = self._card(right, "📝  Văn bản cần ký")
        self.sig_msg_txt = _entry_txt(msg_card, h=5, w=60)
        self.sig_msg_txt.pack(fill="x", padx=12, pady=(0, 10))
        self.sig_msg_txt.insert("1.0", "hello world")

        # Action buttons
        btn_row = tk.Frame(msg_card, bg=WHITE)
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        _btn(btn_row, "✍️  Ký số",    self._sig_sign,
             bg=MS_BLUE).pack(side="left", padx=(0, 8))
        _btn(btn_row, "✅  Xác thực", self._sig_verify,
             bg=SUCCESS_GR).pack(side="left", padx=(0, 8))
        _btn(btn_row, "🗑  Xóa",      self._sig_clear,
             bg="#767676").pack(side="left")

        # Output card
        out_card = self._card(right, "📤  Kết quả")
        self.sig_out_txt = _entry_txt(out_card, h=17, w=60)
        self.sig_out_txt.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        out_card.pack(fill="both", expand=True, pady=(8, 0))

        self._sig_private_key = None
        self._sig_public_key  = None
        self._sig_signature   = None
        self._sig_engine      = None

    def _sig_gen(self):     self._run(self.__sig_gen)
    def _sig_sign(self):    self._run(self.__sig_sign)
    def _sig_verify(self):  self._run(self.__sig_verify)

    def __sig_gen(self):
        self._set_status("⏳ Đang tạo cặp khóa...")
        t0 = time.time()
        curve = EllipticCurve(self.sig_curve_var.get())
        algo  = self.sig_algo_var.get()
        eng   = ECDSA(curve) if algo == "ECDSA" else ECGDSA(curve)
        self._sig_engine = eng
        d, Q  = eng.generate_keypair()
        self._sig_private_key = d
        self._sig_public_key  = Q
        ms = (time.time() - t0) * 1000

        self.sig_priv_txt.delete("1.0", tk.END)
        self.sig_priv_txt.insert(tk.END, str(d))
        self.sig_pub_txt.delete("1.0", tk.END)
        self.sig_pub_txt.insert(tk.END, f"x = {Q.x}\ny = {Q.y}")
        self.sig_time_var.set(f"⏱  {ms:.1f} ms")

        c = curve
        self.sig_out_txt.delete("1.0", tk.END)
        self._out(self.sig_out_txt,
            f"{'═'*52}\n"
            f"  THAM SỐ ĐƯỜNG CONG — {self.sig_curve_var.get()}\n"
            f"{'═'*52}\n"
            f"  p  = {c.p}\n"
            f"  a  = {c.a}\n"
            f"  b  = {c.b}\n"
            f"  Gx = {c.G.x}\n"
            f"  Gy = {c.G.y}\n"
            f"  n  = {c.n}\n"
            f"  h  = {c.h}\n\n"
            f"{'═'*52}\n"
            f"  CẶP KHÓA ({algo})\n"
            f"{'═'*52}\n"
            f"  d  = {d}\n"
            f"  Qx = {Q.x}\n"
            f"  Qy = {Q.y}\n\n"
            f"  ✅ Tạo khóa thành công ({ms:.1f} ms)\n"
            f"  [CSPRNG: secrets.randbelow — bảo mật mật mã học]\n"
        )
        self._set_status(f"✅  Tạo cặp khóa thành công — {algo} / {self.sig_curve_var.get()} ({ms:.1f} ms)")

    def __sig_sign(self):
        if not self._sig_private_key:
            messagebox.showwarning("Chưa có khóa", "Vui lòng tạo cặp khóa trước!"); return
        msg = self.sig_msg_txt.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showwarning("Thiếu nội dung", "Vui lòng nhập văn bản cần ký!"); return
        self._set_status("⏳ Đang ký số...")
        t0 = time.time()
        r, s = self._sig_engine.sign(msg, self._sig_private_key)
        self._sig_signature = (r, s)
        ms = (time.time() - t0) * 1000
        self.sig_out_txt.delete("1.0", tk.END)
        self._out(self.sig_out_txt,
            f"{'═'*52}\n"
            f"  CHỮ KÝ SỐ — {self.sig_algo_var.get()}\n"
            f"{'═'*52}\n"
            f"  Văn bản : {msg[:60]}{'...' if len(msg)>60 else ''}\n\n"
            f"  r = {r}\n\n"
            f"  s = {s}\n\n"
            f"  ⏱  Ký trong {ms:.1f} ms\n"
            f"  👉 Nhấn 'Xác thực' để kiểm tra chữ ký.\n"
        )
        self._set_status(f"✅  Ký số thành công ({ms:.1f} ms)")

    def __sig_verify(self):
        if not self._sig_signature:
            messagebox.showwarning("Chưa ký", "Vui lòng ký văn bản trước!"); return
        msg = self.sig_msg_txt.get("1.0", tk.END).strip()
        self._set_status("⏳ Đang xác thực...")
        t0 = time.time()
        ok = self._sig_engine.verify(msg, self._sig_signature, self._sig_public_key)
        ms = (time.time() - t0) * 1000
        res = "✅  HỢP LỆ — Chữ ký đúng!" if ok else "❌  KHÔNG HỢP LỆ — Chữ ký sai!"
        self.sig_out_txt.insert(tk.END,
            f"\n{'─'*52}\n"
            f"  KẾT QUẢ XÁC THỰC\n"
            f"{'─'*52}\n"
            f"  {res}\n"
            f"  ⏱  {ms:.1f} ms\n"
        )
        self.sig_out_txt.see(tk.END)
        self._set_status(f"{'✅' if ok else '❌'}  Xác thực: {'HỢP LỆ' if ok else 'KHÔNG HỢP LỆ'} ({ms:.1f} ms)")

    def _sig_clear(self):
        self.sig_out_txt.delete("1.0", tk.END)
        self.sig_priv_txt.delete("1.0", tk.END)
        self.sig_pub_txt.delete("1.0", tk.END)
        self.sig_time_var.set("")
        self._sig_private_key = self._sig_public_key = self._sig_signature = None

    # ══════════════════════════════════════════════════
    #  TAB 2 — EC ElGamal
    # ══════════════════════════════════════════════════
    def _build_tab_enc(self, parent):
        # LEFT
        left = tk.Frame(parent, bg=WHITE,
                        highlightthickness=1, highlightbackground=GRAY_BORDER)
        left.pack(side="left", fill="y", padx=(0, 8))

        ptitle = tk.Frame(left, bg=MS_BLUE)
        ptitle.pack(fill="x")
        tk.Label(ptitle, text="⚙️  Cấu hình mã hóa",
                 bg=MS_BLUE, fg=WHITE,
                 font=("Segoe UI Semibold", 10),
                 padx=12, pady=8).pack(anchor="w")

        body = tk.Frame(left, bg=WHITE)
        body.pack(fill="both", padx=14, pady=10)

        self._lbl(body, "Đường cong Elliptic:").grid(
            row=0, column=0, sticky="w", pady=(0, 2))
        self.enc_curve_var = tk.StringVar(value="secp112r1")
        ttk.Combobox(body, textvariable=self.enc_curve_var,
                     values=get_available_curves(ecdsa_only=False),
                     width=20, state="readonly",
                     font=FONT_LABEL).grid(row=1, column=0, sticky="ew", pady=(0, 10))

        _btn(body, "🔑  Tạo khóa Bob",
             lambda: self._run(self.__enc_gen), bg=MS_BLUE,
             pad_x=12, pad_y=7).grid(row=2, column=0, sticky="ew", pady=(4, 12))

        tk.Frame(body, bg=GRAY_BORDER, height=1).grid(
            row=3, column=0, sticky="ew", pady=(0, 10))

        self._lbl(body, "Khóa riêng Bob (s):").grid(
            row=4, column=0, sticky="w", pady=(0, 2))
        self.enc_priv_txt = _entry_txt(body, h=3, w=34)
        self.enc_priv_txt.grid(row=5, column=0, sticky="ew", pady=(0, 8))

        self._lbl(body, "Khóa công khai Bob (B):").grid(
            row=6, column=0, sticky="w", pady=(0, 2))
        self.enc_pub_txt = _entry_txt(body, h=4, w=34)
        self.enc_pub_txt.grid(row=7, column=0, sticky="ew", pady=(0, 6))

        self.enc_time_var = tk.StringVar()
        tk.Label(body, textvariable=self.enc_time_var,
                 bg=WHITE, fg=MS_BLUE, font=("Segoe UI", 8)).grid(
            row=8, column=0, sticky="w")

        # RIGHT
        right = tk.Frame(parent, bg=GRAY_BG)
        right.pack(side="left", fill="both", expand=True)

        msg_card = self._card(right, "📝  Văn bản Alice gửi Bob")
        self.enc_msg_txt = _entry_txt(msg_card, h=5, w=60)
        self.enc_msg_txt.pack(fill="x", padx=12, pady=(0, 10))
        self.enc_msg_txt.insert("1.0", "hello world")

        btn_row = tk.Frame(msg_card, bg=WHITE)
        btn_row.pack(fill="x", padx=12, pady=(0, 12))
        _btn(btn_row, "🔐  Mã hóa",
             lambda: self._run(self.__enc_encrypt),
             bg=MS_BLUE).pack(side="left", padx=(0, 8))
        _btn(btn_row, "🔓  Giải mã",
             lambda: self._run(self.__enc_decrypt),
             bg=SUCCESS_GR).pack(side="left")

        out_card = self._card(right, "📤  Kết quả")
        self.enc_out_txt = _entry_txt(out_card, h=17, w=60)
        self.enc_out_txt.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        out_card.pack(fill="both", expand=True, pady=(8, 0))

        self._enc_priv = self._enc_pub = None
        self._enc_ct = self._enc_M = self._enc_eng = None

    def __enc_gen(self):
        self._set_status("⏳ Tạo khóa Bob...")
        t0 = time.time()
        curve = EllipticCurve(self.enc_curve_var.get())
        self._enc_eng = ECElGamal(curve)
        s, B = self._enc_eng.generate_keypair()
        self._enc_priv, self._enc_pub = s, B
        ms = (time.time() - t0) * 1000
        self.enc_priv_txt.delete("1.0", tk.END)
        self.enc_priv_txt.insert(tk.END, str(s))
        self.enc_pub_txt.delete("1.0", tk.END)
        self.enc_pub_txt.insert(tk.END, f"x = {B.x}\ny = {B.y}")
        self.enc_time_var.set(f"⏱  {ms:.1f} ms")
        self.enc_out_txt.delete("1.0", tk.END)
        self._out(self.enc_out_txt,
            f"✅ Đã tạo cặp khóa Bob ({self.enc_curve_var.get()}) — {ms:.1f} ms\n\n"
            f"  s (private) = {s}\n"
            f"  B.x = {B.x}\n"
            f"  B.y = {B.y}\n"
        )
        self._set_status(f"✅  Tạo khóa Bob thành công ({ms:.1f} ms)")

    def __enc_encrypt(self):
        if not self._enc_pub:
            messagebox.showwarning("Chưa có khóa", "Vui lòng tạo khóa Bob trước!"); return
        msg = self.enc_msg_txt.get("1.0", tk.END).strip()
        if not msg: return
        self._set_status("⏳ Đang mã hóa...")
        t0 = time.time()
        (M1, M2), M = self._enc_eng.encrypt(msg, self._enc_pub)
        self._enc_ct, self._enc_M = (M1, M2), M
        ms = (time.time() - t0) * 1000
        self.enc_out_txt.delete("1.0", tk.END)
        self._out(self.enc_out_txt,
            f"{'═'*52}\n"
            f"  MÃ HÓA EC ELGAMAL\n"
            f"{'═'*52}\n"
            f"  Văn bản gốc : \"{msg}\"\n\n"
            f"  Điểm M nhúng:\n"
            f"    x = {M.x}\n"
            f"    y = {M.y}\n\n"
            f"  Bản mã (M1, M2):\n"
            f"    M1.x = {M1.x}\n"
            f"    M1.y = {M1.y}\n"
            f"    M2.x = {M2.x}\n"
            f"    M2.y = {M2.y}\n\n"
            f"  ⏱  Mã hóa trong {ms:.1f} ms\n"
        )
        self._set_status(f"✅  Mã hóa thành công ({ms:.1f} ms)")

    def __enc_decrypt(self):
        if not self._enc_ct:
            messagebox.showwarning("Chưa mã hóa", "Vui lòng mã hóa trước!"); return
        self._set_status("⏳ Đang giải mã...")
        t0 = time.time()
        Md = self._enc_eng.decrypt(self._enc_ct, self._enc_priv)
        ms = (time.time() - t0) * 1000
        ok = self._enc_eng.points_equal(Md, self._enc_M)
        self.enc_out_txt.insert(tk.END,
            f"\n{'─'*52}\n"
            f"  GIẢI MÃ\n"
            f"{'─'*52}\n"
            f"  M giải mã:\n    x = {Md.x}\n    y = {Md.y}\n\n"
            f"  {'✅  Giải mã THÀNH CÔNG — điểm trùng khớp' if ok else '❌  Điểm KHÔNG khớp!'}\n"
            f"  Văn bản gốc: \"{self.enc_msg_txt.get('1.0', tk.END).strip()}\"\n"
            f"  ⏱  {ms:.1f} ms\n"
        )
        self.enc_out_txt.see(tk.END)
        self._set_status(f"{'✅' if ok else '❌'}  Giải mã {'thành công' if ok else 'thất bại'} ({ms:.1f} ms)")

    # ══════════════════════════════════════════════════
    #  TAB 3 — AI IP Guardian
    # ══════════════════════════════════════════════════
    def _build_tab_guard(self, parent):
        # ── Control bar ───────────────────────────────
        ctrl = tk.Frame(parent, bg=WHITE,
                        highlightthickness=1, highlightbackground=GRAY_BORDER)
        ctrl.pack(fill="x", pady=(0, 8))

        hdr = tk.Frame(ctrl, bg=MS_BLUE)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🤖  AI IP Guardian — Phát hiện & Chặn IP nghi vấn",
                 bg=MS_BLUE, fg=WHITE,
                 font=("Segoe UI Semibold", 10),
                 padx=12, pady=7).pack(side="left")
        tk.Label(hdr,
                 text="Isolation Forest  |  Hard Rules  |  Whitelist",
                 bg=MS_BLUE, fg="#BDD9F2",
                 font=("Segoe UI", 8)).pack(side="right", padx=12)

        row1 = tk.Frame(ctrl, bg=WHITE)
        row1.pack(fill="x", padx=12, pady=8)

        # IP input
        tk.Label(row1, text="IP:", bg=WHITE, fg=GRAY_TEXT,
                 font=FONT_BODY).pack(side="left")
        self.gd_ip_var = tk.StringVar(value="192.168.1.100")
        tk.Entry(row1, textvariable=self.gd_ip_var, width=18,
                 bg=ENTRY_BG, fg=GRAY_TEXT, relief="solid", bd=1,
                 font=FONT_MONO,
                 highlightthickness=1, highlightcolor=MS_BLUE,
                 highlightbackground=GRAY_BORDER).pack(side="left", padx=(4, 12))

        tk.Label(row1, text="Message:", bg=WHITE, fg=GRAY_TEXT,
                 font=FONT_BODY).pack(side="left")
        self.gd_msg_var = tk.StringVar(value="sign_request")
        tk.Entry(row1, textvariable=self.gd_msg_var, width=20,
                 bg=ENTRY_BG, fg=GRAY_TEXT, relief="solid", bd=1,
                 font=FONT_MONO).pack(side="left", padx=(4, 12))

        self.gd_ok_var = tk.BooleanVar(value=True)
        ck = tk.Checkbutton(row1, text="Success", variable=self.gd_ok_var,
                            bg=WHITE, fg=GRAY_TEXT, selectcolor=WHITE,
                            activebackground=WHITE, font=FONT_BODY)
        ck.pack(side="left", padx=(0, 14))

        # Buttons
        for txt, cmd, col in [
            ("🔍  Kiểm tra",          self._gd_check,  MS_BLUE),
            ("⚡  Mô phỏng tấn công", lambda: self._run(self.__gd_sim), MS_RED),
            ("➕  Whitelist",          self._gd_wl,     SUCCESS_GR),
            ("🔄  Reset IP",           self._gd_reset,  "#767676"),
            ("🚫  Xem Blocked",        self._gd_show_blocked, WARN_OR),
        ]:
            _btn(row1, txt, cmd, bg=col, pad_x=10, pad_y=5).pack(
                side="left", padx=3)

        # ── Stats strip ───────────────────────────────
        self.gd_stat_var = tk.StringVar(value="Chưa có thống kê")
        stat_bar = tk.Frame(ctrl, bg="#EEF4FB")
        stat_bar.pack(fill="x")
        tk.Label(stat_bar, textvariable=self.gd_stat_var,
                 bg="#EEF4FB", fg=MS_BLUE,
                 font=("Segoe UI", 8), anchor="w",
                 padx=12, pady=4).pack(fill="x")

        # ── Log area ──────────────────────────────────
        log_card = self._card(parent, "📋  Nhật ký sự kiện")
        self.gd_log = _entry_txt(log_card, h=20, w=100)
        self.gd_log.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        log_card.pack(fill="both", expand=True)

    def _gd_log(self, msg):
        self.gd_log.insert(tk.END, msg + "\n")
        self.gd_log.see(tk.END)

    def _gd_check(self):
        ip  = self.gd_ip_var.get().strip()
        msg = self.gd_msg_var.get().strip()
        ok  = self.gd_ok_var.get()
        res = self.guardian.check(ip, success=ok, message=msg)
        icon = {"allow": "✅", "warn": "⚠️", "block": "🚫"}.get(res["status"], "?")
        ts   = time.strftime("%H:%M:%S")
        self._gd_log(
            f"[{ts}] {icon} {res['status'].upper():6s}  "
            f"IP={ip:<20} Layer={res['layer']:<12} "
            f"Score={res['score']:.3f}  — {res['reason']}"
        )
        s = self.guardian.get_stats(ip)
        self.gd_stat_var.set(
            f"IP {ip}  →  "
            f"Tổng: {s['total']}   Fail: {s['fail']}   "
            f"Fail rate: {s['fail_rate']:.0%}   "
            f"Unique msg: {s['unique_msgs']}   "
            f"Blocked: {'🚫 CÓ' if s['is_blocked'] else '✅ Không'}"
        )
        self._set_status(f"{icon}  IP {ip} — {res['status'].upper()} ({res['reason']})")

    def __gd_sim(self):
        import random
        attacker = self.gd_ip_var.get().strip() or "10.0.0.99"
        self._gd_log(f"\n{'─'*70}")
        self._gd_log(f"  ⚡ Mô phỏng tấn công từ {attacker} (70 request, 90% thất bại)")
        self._gd_log(f"{'─'*70}")
        for i in range(70):
            ok  = random.random() > 0.9
            res = self.guardian.check(attacker, success=ok, message=f"msg_{i}")
            ts  = time.strftime("%H:%M:%S")
            icon = {"allow": "✅", "warn": "⚠️", "block": "🚫"}.get(res["status"], "?")
            self._gd_log(
                f"  [{ts}] req#{i+1:02d}  {icon} {res['status']:6s}  "
                f"score={res['score']:.3f}  {res['reason']}"
            )
            if res["status"] == "block":
                self._gd_log(
                    f"\n  🚫 IP {attacker} BỊ CHẶN sau {i+1} request!  "
                    f"Layer: {res['layer']}")
                break
            time.sleep(0.04)
        self._gd_log(f"{'─'*70}\n")
        self._set_status(f"🚫  Mô phỏng xong — IP {attacker} bị chặn")

    def _gd_wl(self):
        ip = self.gd_ip_var.get().strip()
        self.guardian.add_to_whitelist(ip)
        self._gd_log(f"  [WHITELIST] ➕ Đã thêm {ip} vào danh sách tin cậy")
        self._set_status(f"➕  Đã whitelist {ip}")

    def _gd_reset(self):
        ip = self.gd_ip_var.get().strip()
        self.guardian.reset_ip(ip)
        self._gd_log(f"  [RESET] 🔄 Đã reset toàn bộ lịch sử và trạng thái block: {ip}")
        self._set_status(f"🔄  Reset {ip} thành công")

    def _gd_show_blocked(self):
        blocked = self.guardian.get_blocked_list()
        self._gd_log(f"\n{'─'*70}")
        self._gd_log(f"  🚫 Danh sách IP đang bị chặn ({len(blocked)} IP):")
        if not blocked:
            self._gd_log("  (trống — không có IP nào bị chặn)")
        else:
            for ip, info in blocked.items():
                t = time.strftime("%H:%M:%S", time.localtime(info["time"]))
                self._gd_log(
                    f"  {ip:<22} Layer={info['layer']:<12} "
                    f"Lúc={t}  — {info['reason']}"
                )
        self._gd_log(f"{'─'*70}\n")

    # ══════════════════════════════════════════════════
    #  WIDGET HELPERS
    # ══════════════════════════════════════════════════
    def _lbl(self, parent, text):
        return tk.Label(parent, text=text, bg=WHITE,
                        fg=GRAY_MUTED, font=FONT_LABEL)

    def _card(self, parent, title):
        """Thẻ trắng với tiêu đề xanh Microsoft."""
        card = tk.Frame(parent, bg=WHITE,
                        highlightthickness=1, highlightbackground=GRAY_BORDER)
        card.pack(fill="x")
        hdr = tk.Frame(card, bg="#EEF4FB")
        hdr.pack(fill="x")
        tk.Label(hdr, text=title, bg="#EEF4FB",
                 fg=MS_BLUE, font=("Segoe UI Semibold", 9),
                 padx=12, pady=6).pack(anchor="w")
        tk.Frame(card, bg=GRAY_BORDER, height=1).pack(fill="x")
        return card

    def _out(self, widget, text):
        widget.insert(tk.END, text)
        widget.see(tk.END)


# ── Entry point ───────────────────────────────────────
def run():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    run()
