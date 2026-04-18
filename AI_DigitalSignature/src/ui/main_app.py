# main_app.py — Giao diện Tkinter cho AI-ECDSA Digital Signature System

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os

# Đường dẫn
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.core.elliptic_curve import EllipticCurve, get_available_curves
from src.core.ecdsa import ECDSA, ECGDSA
from src.core.ec_elgamal import ECElGamal
from src.ai.ip_guardian import IPGuardian


# ══════════════════════════════════════════════════════
# Màu sắc & Style
# ══════════════════════════════════════════════════════
BG         = "#1e1e2e"
PANEL      = "#2a2a3e"
ACCENT     = "#7c3aed"
ACCENT2    = "#06b6d4"
SUCCESS    = "#10b981"
WARNING    = "#f59e0b"
DANGER     = "#ef4444"
FG         = "#e2e8f0"
FG_MUTED   = "#94a3b8"
ENTRY_BG   = "#0f172a"
BTN_FG     = "#ffffff"

FONT_TITLE = ("Consolas", 14, "bold")
FONT_BODY  = ("Consolas", 10)
FONT_SMALL = ("Consolas", 9)
FONT_MONO  = ("Courier New", 9)


def style_btn(btn, color=ACCENT):
    btn.configure(
        bg=color, fg=BTN_FG,
        activebackground=color, activeforeground=BTN_FG,
        relief="flat", cursor="hand2",
        padx=10, pady=6, font=FONT_BODY
    )


def make_label(parent, text, color=FG_MUTED, font=FONT_SMALL, **kw):
    return tk.Label(parent, text=text, bg=PANEL, fg=color, font=font, **kw)


def make_entry(parent, width=45, show=""):
    e = tk.Entry(parent, width=width, bg=ENTRY_BG, fg=FG,
                 insertbackground=FG, relief="flat", font=FONT_MONO, show=show)
    return e


def make_text(parent, height=6, width=60):
    t = scrolledtext.ScrolledText(
        parent, height=height, width=width,
        bg=ENTRY_BG, fg=FG, insertbackground=FG,
        relief="flat", font=FONT_MONO, wrap=tk.WORD
    )
    return t


# ══════════════════════════════════════════════════════
# Cửa sổ chính
# ══════════════════════════════════════════════════════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI-ECDSA Digital Signature System")
        self.configure(bg=BG)
        self.geometry("1100x760")
        self.resizable(True, True)

        self.guardian = IPGuardian()

        self._build_header()
        self._build_notebook()
        self._build_status_bar()

    # ── Header ────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=ACCENT, height=50)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text="🔐  AI-ECDSA Digital Signature System",
            bg=ACCENT, fg=BTN_FG,
            font=("Consolas", 15, "bold")
        ).pack(side="left", padx=20, pady=10)
        tk.Label(
            hdr,
            text="Khóa luận tốt nghiệp — Nguyễn Duy Cao",
            bg=ACCENT, fg="#ddd6fe",
            font=FONT_SMALL
        ).pack(side="right", padx=20)

    # ── Notebook (3 tab) ──────────────────────────────
    def _build_notebook(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook",           background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",       background=PANEL, foreground=FG_MUTED,
                        font=FONT_BODY, padding=[14, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", BTN_FG)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=10)

        self.tab_sig    = tk.Frame(nb, bg=BG)
        self.tab_enc    = tk.Frame(nb, bg=BG)
        self.tab_guard  = tk.Frame(nb, bg=BG)

        nb.add(self.tab_sig,   text="🔏  Chữ ký số (ECDSA / ECGDSA)")
        nb.add(self.tab_enc,   text="🔒  Mã hóa EC ElGamal")
        nb.add(self.tab_guard, text="🤖  AI IP Guardian")

        self._build_tab_signature(self.tab_sig)
        self._build_tab_elgamal(self.tab_enc)
        self._build_tab_guardian(self.tab_guard)

    # ── Status bar ────────────────────────────────────
    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="✅  Sẵn sàng")
        bar = tk.Label(self, textvariable=self.status_var,
                       bg=PANEL, fg=SUCCESS, font=FONT_SMALL,
                       anchor="w", padx=12, pady=4)
        bar.pack(fill="x", side="bottom")

    def _set_status(self, msg, color=SUCCESS):
        self.status_var.set(msg)
        bar = self.nametowidget(self.status_var)
        try:
            bar.configure(fg=color)
        except Exception:
            pass

    # ══════════════════════════════════════════════════
    # TAB 1 — Chữ ký số
    # ══════════════════════════════════════════════════

    def _build_tab_signature(self, parent):
        # ── left panel ──
        left = tk.Frame(parent, bg=PANEL, bd=0)
        left.pack(side="left", fill="y", padx=(12, 6), pady=12, ipadx=10, ipady=10)

        tk.Label(left, text="⚙️  Cấu hình", bg=PANEL, fg=ACCENT2,
                 font=FONT_TITLE).grid(row=0, column=0, columnspan=2,
                                       sticky="w", padx=8, pady=(8, 4))

        # Chọn đường cong
        make_label(left, "Đường cong:").grid(row=1, column=0, sticky="w", padx=8)
        self.sig_curve_var = tk.StringVar(value="secp112r1")
        curve_cb = ttk.Combobox(left, textvariable=self.sig_curve_var,
                                values=get_available_curves(), width=18, state="readonly")
        curve_cb.grid(row=1, column=1, sticky="w", padx=8, pady=3)

        # Chọn thuật toán
        make_label(left, "Thuật toán:").grid(row=2, column=0, sticky="w", padx=8)
        self.sig_algo_var = tk.StringVar(value="ECDSA")
        for i, algo in enumerate(["ECDSA", "ECGDSA"]):
            tk.Radiobutton(left, text=algo, variable=self.sig_algo_var, value=algo,
                           bg=PANEL, fg=FG, selectcolor=PANEL, activebackground=PANEL,
                           font=FONT_BODY).grid(row=2, column=1+i, sticky="w", padx=4, pady=3)

        # Nút tạo khóa
        btn_gen = tk.Button(left, text="🔑  Tạo cặp khóa",
                            command=self._sig_generate_keys)
        style_btn(btn_gen, ACCENT)
        btn_gen.grid(row=3, column=0, columnspan=3, pady=(10, 4), padx=8, sticky="ew")

        # Private key
        make_label(left, "Khóa riêng (d):").grid(row=4, column=0, columnspan=3,
                                                   sticky="w", padx=8, pady=(8, 0))
        self.sig_priv_txt = make_text(left, height=3, width=38)
        self.sig_priv_txt.grid(row=5, column=0, columnspan=3, padx=8, pady=2)

        # Public key
        make_label(left, "Khóa công khai (Q):").grid(row=6, column=0, columnspan=3,
                                                      sticky="w", padx=8, pady=(6, 0))
        self.sig_pub_txt = make_text(left, height=4, width=38)
        self.sig_pub_txt.grid(row=7, column=0, columnspan=3, padx=8, pady=2)

        # Thời gian
        self.sig_keytime_var = tk.StringVar()
        tk.Label(left, textvariable=self.sig_keytime_var, bg=PANEL,
                 fg=FG_MUTED, font=FONT_SMALL).grid(row=8, column=0, columnspan=3, padx=8)

        # ── right panel ──
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(6, 12), pady=12)

        # Message
        tk.Label(right, text="📝  Văn bản cần ký:", bg=BG, fg=FG,
                 font=FONT_BODY).pack(anchor="w", padx=4)
        self.sig_msg_txt = make_text(right, height=5, width=65)
        self.sig_msg_txt.pack(fill="x", padx=4, pady=(2, 8))
        self.sig_msg_txt.insert("1.0", "hello world")

        # Nút ký / xác thực
        btn_frame = tk.Frame(right, bg=BG)
        btn_frame.pack(fill="x", padx=4, pady=4)
        btn_sign = tk.Button(btn_frame, text="✍️  Ký số", command=self._sig_sign)
        style_btn(btn_sign, ACCENT)
        btn_sign.pack(side="left", padx=6)
        btn_verify = tk.Button(btn_frame, text="✅  Xác thực", command=self._sig_verify)
        style_btn(btn_verify, SUCCESS)
        btn_verify.pack(side="left", padx=6)
        btn_clear = tk.Button(btn_frame, text="🗑  Xóa", command=self._sig_clear)
        style_btn(btn_clear, "#475569")
        btn_clear.pack(side="left", padx=6)

        # Output
        tk.Label(right, text="📤  Kết quả:", bg=BG, fg=FG,
                 font=FONT_BODY).pack(anchor="w", padx=4, pady=(10, 2))
        self.sig_out_txt = make_text(right, height=18, width=65)
        self.sig_out_txt.pack(fill="both", expand=True, padx=4)

        # State
        self._sig_private_key = None
        self._sig_public_key  = None
        self._sig_signature   = None
        self._sig_curve       = None

    def _run_in_thread(self, fn, *args):
        t = threading.Thread(target=fn, args=args, daemon=True)
        t.start()

    def _sig_generate_keys(self):
        self._run_in_thread(self.__sig_generate_keys)

    def __sig_generate_keys(self):
        self.sig_out_txt.delete("1.0", tk.END)
        self.sig_out_txt.insert(tk.END, "⏳ Đang tạo cặp khóa...\n")

        t0 = time.time()
        curve_name = self.sig_curve_var.get()
        self._sig_curve = EllipticCurve(curve_name)

        algo = self.sig_algo_var.get()
        if algo == "ECDSA":
            engine = ECDSA(self._sig_curve)
        else:
            engine = ECGDSA(self._sig_curve)
        self._sig_engine = engine

        d, Q = engine.generate_keypair()
        self._sig_private_key = d
        self._sig_public_key  = Q
        elapsed = time.time() - t0

        self.sig_priv_txt.delete("1.0", tk.END)
        self.sig_priv_txt.insert(tk.END, str(d))

        self.sig_pub_txt.delete("1.0", tk.END)
        self.sig_pub_txt.insert(tk.END, f"x = {Q.x}\ny = {Q.y}")

        self.sig_keytime_var.set(f"⏱ Tạo khóa: {elapsed*1000:.1f} ms")

        self.sig_out_txt.delete("1.0", tk.END)
        c = self._sig_curve
        info = (
            f"=== Tham số đường cong {curve_name} ===\n"
            f"p = {c.p}\n"
            f"a = {c.a}\n"
            f"b = {c.b}\n"
            f"Gx= {c.G.x}\n"
            f"Gy= {c.G.y}\n"
            f"n = {c.n}\n"
            f"h = {c.h}\n\n"
            f"=== Cặp khóa ({algo}) ===\n"
            f"Khóa riêng d  = {d}\n"
            f"Khóa công khai:\n  x = {Q.x}\n  y = {Q.y}\n\n"
            f"✅ Tạo khóa thành công trong {elapsed*1000:.1f} ms"
        )
        self.sig_out_txt.insert(tk.END, info)

    def _sig_sign(self):
        self._run_in_thread(self.__sig_sign)

    def __sig_sign(self):
        if self._sig_private_key is None:
            messagebox.showwarning("Chưa tạo khóa", "Vui lòng tạo cặp khóa trước!")
            return
        msg = self.sig_msg_txt.get("1.0", tk.END).strip()
        if not msg:
            messagebox.showwarning("Thiếu văn bản", "Vui lòng nhập văn bản cần ký!")
            return

        t0 = time.time()
        r, s = self._sig_engine.sign(msg, self._sig_private_key)
        self._sig_signature = (r, s)
        elapsed = time.time() - t0

        self.sig_out_txt.delete("1.0", tk.END)
        self.sig_out_txt.insert(tk.END,
            f"=== Chữ ký số ({self.sig_algo_var.get()}) ===\n"
            f"r = {r}\n"
            f"s = {s}\n\n"
            f"⏱ Ký trong {elapsed*1000:.1f} ms\n\n"
            f"👉 Nhấn 'Xác thực' để kiểm tra chữ ký."
        )

    def _sig_verify(self):
        self._run_in_thread(self.__sig_verify)

    def __sig_verify(self):
        if self._sig_signature is None:
            messagebox.showwarning("Chưa ký", "Vui lòng ký văn bản trước!")
            return
        msg = self.sig_msg_txt.get("1.0", tk.END).strip()

        t0 = time.time()
        ok = self._sig_engine.verify(msg, self._sig_signature, self._sig_public_key)
        elapsed = time.time() - t0

        result = "✅ HỢP LỆ" if ok else "❌ KHÔNG HỢP LỆ"
        color_line = "=" * 50
        self.sig_out_txt.insert(tk.END,
            f"\n{color_line}\n"
            f"Kết quả xác thực: {result}\n"
            f"⏱ Xác thực trong {elapsed*1000:.1f} ms\n"
            f"{color_line}\n"
        )

    def _sig_clear(self):
        self.sig_out_txt.delete("1.0", tk.END)
        self._sig_private_key = None
        self._sig_public_key  = None
        self._sig_signature   = None
        self.sig_priv_txt.delete("1.0", tk.END)
        self.sig_pub_txt.delete("1.0", tk.END)
        self.sig_keytime_var.set("")

    # ══════════════════════════════════════════════════
    # TAB 2 — EC ElGamal
    # ══════════════════════════════════════════════════

    def _build_tab_elgamal(self, parent):
        left = tk.Frame(parent, bg=PANEL)
        left.pack(side="left", fill="y", padx=(12, 6), pady=12, ipadx=10, ipady=10)

        tk.Label(left, text="⚙️  Cấu hình", bg=PANEL, fg=ACCENT2,
                 font=FONT_TITLE).grid(row=0, column=0, columnspan=2,
                                       sticky="w", padx=8, pady=(8, 4))

        make_label(left, "Đường cong:").grid(row=1, column=0, sticky="w", padx=8)
        self.enc_curve_var = tk.StringVar(value="secp112r1")
        ttk.Combobox(left, textvariable=self.enc_curve_var,
                     values=get_available_curves(), width=18,
                     state="readonly").grid(row=1, column=1, sticky="w", padx=8, pady=3)

        btn_gen = tk.Button(left, text="🔑  Tạo khóa Bob",
                            command=lambda: self._run_in_thread(self.__enc_gen_keys))
        style_btn(btn_gen, ACCENT)
        btn_gen.grid(row=2, column=0, columnspan=2, pady=(10, 4), padx=8, sticky="ew")

        make_label(left, "Khóa riêng (s):").grid(row=3, column=0, columnspan=2,
                                                   sticky="w", padx=8, pady=(8, 0))
        self.enc_priv_txt = make_text(left, height=3, width=38)
        self.enc_priv_txt.grid(row=4, column=0, columnspan=2, padx=8, pady=2)

        make_label(left, "Khóa công khai (B):").grid(row=5, column=0, columnspan=2,
                                                      sticky="w", padx=8, pady=(6, 0))
        self.enc_pub_txt = make_text(left, height=4, width=38)
        self.enc_pub_txt.grid(row=6, column=0, columnspan=2, padx=8, pady=2)

        self.enc_keytime_var = tk.StringVar()
        tk.Label(left, textvariable=self.enc_keytime_var, bg=PANEL,
                 fg=FG_MUTED, font=FONT_SMALL).grid(row=7, column=0, columnspan=2, padx=8)

        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True, padx=(6, 12), pady=12)

        tk.Label(right, text="📝  Văn bản (Alice gửi):", bg=BG, fg=FG,
                 font=FONT_BODY).pack(anchor="w", padx=4)
        self.enc_msg_txt = make_text(right, height=4, width=65)
        self.enc_msg_txt.pack(fill="x", padx=4, pady=(2, 8))
        self.enc_msg_txt.insert("1.0", "hello world")

        btn_frame = tk.Frame(right, bg=BG)
        btn_frame.pack(fill="x", padx=4, pady=4)
        tk.Button(btn_frame, text="🔐  Mã hóa",
                  command=lambda: self._run_in_thread(self.__enc_encrypt)
                  ).pack(side="left", padx=6)
        style_btn(btn_frame.winfo_children()[-1], ACCENT)
        tk.Button(btn_frame, text="🔓  Giải mã",
                  command=lambda: self._run_in_thread(self.__enc_decrypt)
                  ).pack(side="left", padx=6)
        style_btn(btn_frame.winfo_children()[-1], SUCCESS)

        tk.Label(right, text="📤  Kết quả:", bg=BG, fg=FG,
                 font=FONT_BODY).pack(anchor="w", padx=4, pady=(10, 2))
        self.enc_out_txt = make_text(right, height=20, width=65)
        self.enc_out_txt.pack(fill="both", expand=True, padx=4)

        self._enc_private_key = None
        self._enc_public_key  = None
        self._enc_ciphertext  = None
        self._enc_curve       = None
        self._enc_plaintext_point = None

    def __enc_gen_keys(self):
        t0 = time.time()
        self._enc_curve = EllipticCurve(self.enc_curve_var.get())
        engine = ECElGamal(self._enc_curve)
        self._enc_engine = engine
        s, B = engine.generate_keypair()
        self._enc_private_key = s
        self._enc_public_key  = B
        elapsed = time.time() - t0

        self.enc_priv_txt.delete("1.0", tk.END)
        self.enc_priv_txt.insert(tk.END, str(s))
        self.enc_pub_txt.delete("1.0", tk.END)
        self.enc_pub_txt.insert(tk.END, f"x = {B.x}\ny = {B.y}")
        self.enc_keytime_var.set(f"⏱ Tạo khóa: {elapsed*1000:.1f} ms")

        self.enc_out_txt.delete("1.0", tk.END)
        self.enc_out_txt.insert(tk.END,
            f"✅ Đã tạo cặp khóa Bob ({self.enc_curve_var.get()}) "
            f"trong {elapsed*1000:.1f} ms\n"
        )

    def __enc_encrypt(self):
        if self._enc_public_key is None:
            messagebox.showwarning("Chưa tạo khóa", "Vui lòng tạo khóa Bob trước!")
            return
        msg = self.enc_msg_txt.get("1.0", tk.END).strip()
        if not msg:
            return
        t0 = time.time()
        (M1, M2), M = self._enc_engine.encrypt(msg, self._enc_public_key)
        self._enc_ciphertext = (M1, M2)
        self._enc_plaintext_point = M
        elapsed = time.time() - t0

        self.enc_out_txt.delete("1.0", tk.END)
        self.enc_out_txt.insert(tk.END,
            f"=== Mã hóa ElGamal ===\n"
            f"Điểm M nhúng:\n  x={M.x}\n  y={M.y}\n\n"
            f"Bản mã (M1, M2):\n"
            f"  M1.x={M1.x}\n  M1.y={M1.y}\n"
            f"  M2.x={M2.x}\n  M2.y={M2.y}\n\n"
            f"⏱ Mã hóa trong {elapsed*1000:.1f} ms\n"
        )

    def __enc_decrypt(self):
        if self._enc_ciphertext is None:
            messagebox.showwarning("Chưa mã hóa", "Vui lòng mã hóa văn bản trước!")
            return
        t0 = time.time()
        M_dec = self._enc_engine.decrypt(self._enc_ciphertext, self._enc_private_key)
        elapsed = time.time() - t0

        ok = self._enc_engine.points_equal(M_dec, self._enc_plaintext_point)
        status = "✅ Giải mã THÀNH CÔNG — điểm trùng khớp" if ok else "❌ Điểm không khớp"

        self.enc_out_txt.insert(tk.END,
            f"\n=== Giải mã ===\n"
            f"Điểm M giải mã:\n  x={M_dec.x}\n  y={M_dec.y}\n\n"
            f"{status}\n"
            f"Văn bản gốc: \"{self.enc_msg_txt.get('1.0', tk.END).strip()}\"\n"
            f"⏱ Giải mã trong {elapsed*1000:.1f} ms\n"
        )

    # ══════════════════════════════════════════════════
    # TAB 3 — AI IP Guardian
    # ══════════════════════════════════════════════════

    def _build_tab_guardian(self, parent):
        # Cấu hình
        top = tk.Frame(parent, bg=PANEL)
        top.pack(fill="x", padx=12, pady=(12, 6), ipady=8, ipadx=8)

        tk.Label(top, text="🤖  AI IP Guardian", bg=PANEL, fg=ACCENT2,
                 font=FONT_TITLE).pack(side="left", padx=12)

        tk.Label(top, text="IP:", bg=PANEL, fg=FG, font=FONT_BODY).pack(side="left", padx=(20, 4))
        self.guard_ip_var = tk.StringVar(value="192.168.1.100")
        tk.Entry(top, textvariable=self.guard_ip_var, width=18,
                 bg=ENTRY_BG, fg=FG, insertbackground=FG, font=FONT_MONO,
                 relief="flat").pack(side="left")

        tk.Label(top, text="Message:", bg=PANEL, fg=FG, font=FONT_BODY).pack(side="left", padx=(14, 4))
        self.guard_msg_var = tk.StringVar(value="test_signature")
        tk.Entry(top, textvariable=self.guard_msg_var, width=20,
                 bg=ENTRY_BG, fg=FG, insertbackground=FG, font=FONT_MONO,
                 relief="flat").pack(side="left")

        self.guard_success_var = tk.BooleanVar(value=True)
        tk.Checkbutton(top, text="Success", variable=self.guard_success_var,
                       bg=PANEL, fg=FG, selectcolor=PANEL, activebackground=PANEL,
                       font=FONT_BODY).pack(side="left", padx=10)

        btn_check = tk.Button(top, text="🔍  Kiểm tra",
                              command=self._guard_check)
        style_btn(btn_check, ACCENT)
        btn_check.pack(side="left", padx=8)

        btn_sim = tk.Button(top, text="⚡  Mô phỏng tấn công",
                            command=lambda: self._run_in_thread(self.__guard_simulate))
        style_btn(btn_sim, DANGER)
        btn_sim.pack(side="left", padx=4)

        btn_wl = tk.Button(top, text="➕  Thêm Whitelist",
                           command=self._guard_add_whitelist)
        style_btn(btn_wl, SUCCESS)
        btn_wl.pack(side="left", padx=4)

        btn_reset = tk.Button(top, text="🔄  Reset IP",
                              command=self._guard_reset)
        style_btn(btn_reset, "#475569")
        btn_reset.pack(side="left", padx=4)

        # Log area
        mid = tk.Frame(parent, bg=BG)
        mid.pack(fill="both", expand=True, padx=12, pady=6)

        tk.Label(mid, text="📋  Nhật ký sự kiện:", bg=BG, fg=FG,
                 font=FONT_BODY).pack(anchor="w")
        self.guard_log_txt = make_text(mid, height=22, width=100)
        self.guard_log_txt.pack(fill="both", expand=True)

        # Stats bar
        self.guard_stats_var = tk.StringVar(value="Chưa có thống kê")
        tk.Label(parent, textvariable=self.guard_stats_var,
                 bg=PANEL, fg=FG_MUTED, font=FONT_SMALL,
                 anchor="w", padx=12, pady=4).pack(fill="x", padx=12)

    def _guard_log(self, msg, color=None):
        self.guard_log_txt.insert(tk.END, msg + "\n")
        self.guard_log_txt.see(tk.END)

    def _guard_check(self):
        ip  = self.guard_ip_var.get().strip()
        msg = self.guard_msg_var.get().strip()
        ok  = self.guard_success_var.get()

        result = self.guardian.check(ip, success=ok, message=msg)
        status_color = {
            "allow": "✅",
            "warn":  "⚠️",
            "block": "🚫",
        }.get(result["status"], "❓")

        ts = time.strftime("%H:%M:%S")
        log = (
            f"[{ts}] {status_color} {result['status'].upper():6s} "
            f"IP={ip:<18} Layer={result['layer']:<12} "
            f"Score={result['score']:.3f}  {result['reason']}"
        )
        self._guard_log(log)

        stats = self.guardian.get_stats(ip)
        self.guard_stats_var.set(
            f"IP {ip} → total={stats['total']}  fail={stats['fail']}  "
            f"fail_rate={stats['fail_rate']:.0%}  unique_msgs={stats['unique_msgs']}"
        )

    def __guard_simulate(self):
        """Mô phỏng tấn công brute-force từ một IP."""
        import random
        attacker = self.guard_ip_var.get().strip() or "10.0.0.99"
        self._guard_log(f"\n{'─'*60}")
        self._guard_log(f"⚡ Bắt đầu mô phỏng tấn công từ {attacker} ...")
        for i in range(70):
            ok = random.random() > 0.9  # 90% thất bại
            result = self.guardian.check(attacker, success=ok, message=f"msg_{i}")
            ts = time.strftime("%H:%M:%S")
            icon = {"allow": "✅", "warn": "⚠️", "block": "🚫"}.get(result["status"], "?")
            self._guard_log(
                f"[{ts}] req#{i+1:02d} {icon} {result['status']:6s} "
                f"score={result['score']:.3f}  {result['reason']}"
            )
            if result["status"] == "block":
                self._guard_log(f"🚫 IP {attacker} đã bị chặn sau {i+1} request!")
                break
            time.sleep(0.05)
        self._guard_log(f"{'─'*60}\n")

    def _guard_add_whitelist(self):
        ip = self.guard_ip_var.get().strip()
        self.guardian.add_to_whitelist(ip)
        self._guard_log(f"[WHITELIST] ➕ Đã thêm {ip} vào danh sách tin cậy")

    def _guard_reset(self):
        ip = self.guard_ip_var.get().strip()
        self.guardian.reset_ip(ip)
        self._guard_log(f"[RESET] 🔄 Đã reset thống kê cho IP {ip}")


# ── Entry point ───────────────────────────────────────

def run():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run()
