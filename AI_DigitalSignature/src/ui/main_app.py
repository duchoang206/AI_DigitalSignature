import customtkinter as ctk
import tkinter.messagebox as messagebox
import threading
import time
import sys
import os
from PIL import Image

# Đảm bảo import core logic
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.core.elliptic_curve import EllipticCurve, get_available_curves
from src.core.ecdsa import ECDSA, ECGDSA
from src.core.ec_elgamal import ECElGamal
from src.ai.ip_guardian import IPGuardian

# ================= Thiết lập Theme Surface City =================
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

SUCCESS_COLOR = "#10b981"
WARNING_COLOR = "#f59e0b"
DANGER_COLOR = "#ef4444"
MUTED_TEXT = "#64748b"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI-ECDSA Digital Signature - Surface City Edition")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(fg_color="#F0F4F8") # Màu nền xám nhạt như Windows 11

        self.guardian = IPGuardian()

        # Chia layout chính: Cột 0 (Sidebar), Cột 1 (Nội dung chính)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main_content()
        
        # Hiển thị trang mặc định đầu tiên
        self.select_frame_by_name("signature")

    # ── Sidebar (Menu bên trái chứa Logo) ─────────────────────────
    def _build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#FFFFFF")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1) # Đẩy các thành phần dưới cùng xuống đáy

        # 1. Khu vực Logo Surface City
        logo_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")
        
        # Tải Logo (Đổi tên file ảnh dưới đây cho đúng với file bạn đang có)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        logo_path = os.path.join(base_dir, "image_2c19ae.png") # <--- ĐIỀN ĐÚNG TÊN FILE ẢNH
        
        try:
            logo_img_data = Image.open(logo_path)
            logo_image = ctk.CTkImage(light_image=logo_img_data, size=(180, 50)) # Chỉnh kích thước logo ở đây
            logo_label = ctk.CTkLabel(logo_frame, image=logo_image, text="")
            logo_label.pack()
        except Exception:
            logo_label = ctk.CTkLabel(logo_frame, text="SURFACE CITY\nSECURITY", font=ctk.CTkFont(size=20, weight="bold"), text_color="#0078D4")
            logo_label.pack()

        # 2. Các nút Menu
        self.btn_signature = ctk.CTkButton(self.sidebar_frame, text="🔏 Chữ ký số (ECDSA)", fg_color="transparent", text_color="#333333", hover_color="#E5F3FF", anchor="w", font=ctk.CTkFont(size=14), command=lambda: self.select_frame_by_name("signature"))
        self.btn_signature.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.btn_elgamal = ctk.CTkButton(self.sidebar_frame, text="🔒 Mã hóa EC ElGamal", fg_color="transparent", text_color="#333333", hover_color="#E5F3FF", anchor="w", font=ctk.CTkFont(size=14), command=lambda: self.select_frame_by_name("elgamal"))
        self.btn_elgamal.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.btn_guardian = ctk.CTkButton(self.sidebar_frame, text="🤖 AI IP Guardian", fg_color="transparent", text_color="#333333", hover_color="#E5F3FF", anchor="w", font=ctk.CTkFont(size=14), command=lambda: self.select_frame_by_name("guardian"))
        self.btn_guardian.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        # 3. Tác giả (dưới cùng)
        author_lbl = ctk.CTkLabel(self.sidebar_frame, text="By Nguyễn Duy Cao\nKhóa luận tốt nghiệp", font=ctk.CTkFont(size=11), text_color=MUTED_TEXT, justify="left")
        author_lbl.grid(row=5, column=0, padx=20, pady=20, sticky="sw")

    # ── Chuyển đổi giữa các màn hình ──────────────────────────────
    def select_frame_by_name(self, name):
        # Đổi màu nút để biết đang ở tab nào
        self.btn_signature.configure(fg_color="#0078D4" if name == "signature" else "transparent", text_color="white" if name == "signature" else "#333333")
        self.btn_elgamal.configure(fg_color="#0078D4" if name == "elgamal" else "transparent", text_color="white" if name == "elgamal" else "#333333")
        self.btn_guardian.configure(fg_color="#0078D4" if name == "guardian" else "transparent", text_color="white" if name == "guardian" else "#333333")

        # Ẩn tất cả frame
        self.frame_signature.grid_forget()
        self.frame_elgamal.grid_forget()
        self.frame_guardian.grid_forget()

        # Hiện frame được chọn
        if name == "signature":
            self.frame_signature.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        elif name == "elgamal":
            self.frame_elgamal.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        elif name == "guardian":
            self.frame_guardian.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    # ── Khởi tạo nội dung các trang ───────────────────────────────
    def _build_main_content(self):
        # Frame 1: Signature
        self.frame_signature = ctk.CTkFrame(self, corner_radius=15, fg_color="#FFFFFF")
        self._build_tab_signature(self.frame_signature)

        # Frame 2: ElGamal
        self.frame_elgamal = ctk.CTkFrame(self, corner_radius=15, fg_color="#FFFFFF")
        self._build_tab_elgamal(self.frame_elgamal)

        # Frame 3: IP Guardian
        self.frame_guardian = ctk.CTkFrame(self, corner_radius=15, fg_color="#FFFFFF")
        self._build_tab_guardian(self.frame_guardian)

    # ==================================================================
    # TAB 1 — Chữ ký số
    # ==================================================================
    def _build_tab_signature(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        # Cột Trái: Cấu hình
        left = ctk.CTkFrame(parent, fg_color="#F8F9FA", width=350, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        left.grid_propagate(False)

        ctk.CTkLabel(left, text="⚙️ Cấu hình", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B").grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(left, text="Đường cong:").grid(row=1, column=0, sticky="w", padx=15, pady=5)
        self.sig_curve_var = ctk.StringVar(value="secp112r1")
        self.curve_cb = ctk.CTkComboBox(left, variable=self.sig_curve_var, values=get_available_curves(ecdsa_only=True), width=180)
        self.curve_cb.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(left, text="Thuật toán:").grid(row=2, column=0, sticky="w", padx=15, pady=5)
        self.sig_algo_var = ctk.StringVar(value="ECDSA")
        algo_frame = ctk.CTkFrame(left, fg_color="transparent")
        algo_frame.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        ctk.CTkRadioButton(algo_frame, text="ECDSA", variable=self.sig_algo_var, value="ECDSA").pack(side="left", padx=(0, 10))
        ctk.CTkRadioButton(algo_frame, text="ECGDSA", variable=self.sig_algo_var, value="ECGDSA").pack(side="left")

        self.btn_gen = ctk.CTkButton(left, text="🔑 Tạo cặp khóa", command=self._sig_generate_keys)
        self.btn_gen.grid(row=3, column=0, columnspan=2, pady=15, padx=15, sticky="ew")

        ctk.CTkLabel(left, text="Khóa riêng (d):").grid(row=4, column=0, columnspan=2, sticky="w", padx=15)
        self.sig_priv_txt = ctk.CTkTextbox(left, height=60, font=ctk.CTkFont("Consolas", 12))
        self.sig_priv_txt.grid(row=5, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(left, text="Khóa công khai (Q):").grid(row=6, column=0, columnspan=2, sticky="w", padx=15)
        self.sig_pub_txt = ctk.CTkTextbox(left, height=80, font=ctk.CTkFont("Consolas", 12))
        self.sig_pub_txt.grid(row=7, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        self.sig_keytime_var = ctk.StringVar()
        ctk.CTkLabel(left, textvariable=self.sig_keytime_var, text_color=MUTED_TEXT, font=ctk.CTkFont(size=11)).grid(row=8, column=0, columnspan=2, padx=15, pady=5)

        # Cột Phải: Xử lý
        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(right, text="📝 Văn bản cần ký:", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1E293B").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.sig_msg_txt = ctk.CTkTextbox(right, height=100, font=ctk.CTkFont("Consolas", 13), fg_color="#F8F9FA", border_width=1, border_color="#E2E8F0")
        self.sig_msg_txt.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.sig_msg_txt.insert("0.0", "Nhập văn bản cần ký tại đây...")

        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="w", pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="✍️ Ký số", command=self._sig_sign, fg_color="#0078D4", hover_color="#005A9E").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="✅ Xác thực", command=self._sig_verify, fg_color=SUCCESS_COLOR, hover_color="#059669").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="🗑 Xóa", command=self._sig_clear, fg_color="#64748b", hover_color="#475569").pack(side="left")

        ctk.CTkLabel(right, text="📤 Kết quả Output:", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1E293B").grid(row=3, column=0, sticky="w", pady=(10, 5))
        self.sig_out_txt = ctk.CTkTextbox(right, font=ctk.CTkFont("Consolas", 13), fg_color="#1E1E1E", text_color="#00FF00") # Terminal xanh đen
        self.sig_out_txt.grid(row=4, column=0, sticky="nsew")

        self._sig_private_key = None
        self._sig_public_key  = None
        self._sig_signature   = None
        self._sig_curve       = None
        self._sig_engine      = None

    def _run_in_thread(self, fn, *args):
        threading.Thread(target=fn, args=args, daemon=True).start()

    # (Giữ nguyên toàn bộ Logic của Tab 1)
    def _sig_generate_keys(self):
        self._run_in_thread(self.__sig_generate_keys)

    def __sig_generate_keys(self):
        self.sig_out_txt.delete("0.0", "end")
        self.sig_out_txt.insert("end", "⏳ Đang tạo cặp khóa...\n")
        t0 = time.time()
        curve_name       = self.sig_curve_var.get()
        self._sig_curve  = EllipticCurve(curve_name)
        algo             = self.sig_algo_var.get()
        engine = ECDSA(self._sig_curve) if algo == "ECDSA" else ECGDSA(self._sig_curve)
        self._sig_engine = engine
        d, Q = engine.generate_keypair()
        self._sig_private_key = d
        self._sig_public_key  = Q
        elapsed = time.time() - t0
        self.sig_priv_txt.delete("0.0", "end")
        self.sig_priv_txt.insert("end", str(d))
        self.sig_pub_txt.delete("0.0", "end")
        self.sig_pub_txt.insert("end", f"x = {Q.x}\ny = {Q.y}")
        self.sig_keytime_var.set(f"⏱ Tạo khóa: {elapsed*1000:.1f} ms")
        c = self._sig_curve
        self.sig_out_txt.delete("0.0", "end")
        self.sig_out_txt.insert("end",
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
            f"✅ Tạo khóa thành công trong {elapsed*1000:.1f} ms\n"
        )

    def _sig_sign(self):
        self._run_in_thread(self.__sig_sign)

    def __sig_sign(self):
        if self._sig_private_key is None:
            messagebox.showwarning("Chưa tạo khóa", "Vui lòng tạo cặp khóa trước!")
            return
        msg = self.sig_msg_txt.get("0.0", "end").strip()
        if not msg:
            messagebox.showwarning("Thiếu văn bản", "Vui lòng nhập văn bản cần ký!")
            return
        t0 = time.time()
        r, s = self._sig_engine.sign(msg, self._sig_private_key)
        self._sig_signature = (r, s)
        elapsed = time.time() - t0
        self.sig_out_txt.delete("0.0", "end")
        self.sig_out_txt.insert("end",
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
        msg = self.sig_msg_txt.get("0.0", "end").strip()
        t0 = time.time()
        ok = self._sig_engine.verify(msg, self._sig_signature, self._sig_public_key)
        elapsed = time.time() - t0
        result = "✅ HỢP LỆ" if ok else "❌ KHÔNG HỢP LỆ"
        self.sig_out_txt.insert("end", f"\n{'='*50}\nKết quả xác thực: {result}\n⏱ Xác thực trong {elapsed*1000:.1f} ms\n{'='*50}\n")

    def _sig_clear(self):
        self.sig_out_txt.delete("0.0", "end")
        self._sig_private_key = None
        self._sig_public_key  = None
        self._sig_signature   = None
        self.sig_priv_txt.delete("0.0", "end")
        self.sig_pub_txt.delete("0.0", "end")
        self.sig_keytime_var.set("")

    # ==================================================================
    # TAB 2 — EC ElGamal
    # ==================================================================
    def _build_tab_elgamal(self, parent):
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(parent, fg_color="#F8F9FA", width=350, corner_radius=10)
        left.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        left.grid_propagate(False)

        ctk.CTkLabel(left, text="⚙️ Cấu hình", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B").grid(row=0, column=0, columnspan=2, sticky="w", padx=15, pady=(15, 10))

        ctk.CTkLabel(left, text="Đường cong:").grid(row=1, column=0, sticky="w", padx=15, pady=5)
        self.enc_curve_var = ctk.StringVar(value="secp112r1")
        ctk.CTkComboBox(left, variable=self.enc_curve_var, values=get_available_curves(ecdsa_only=False), width=180).grid(row=1, column=1, sticky="w", padx=10, pady=5)

        ctk.CTkButton(left, text="🔑 Tạo khóa Bob", command=lambda: self._run_in_thread(self.__enc_gen_keys)).grid(row=2, column=0, columnspan=2, pady=15, padx=15, sticky="ew")

        ctk.CTkLabel(left, text="Khóa riêng (s):").grid(row=3, column=0, columnspan=2, sticky="w", padx=15)
        self.enc_priv_txt = ctk.CTkTextbox(left, height=60, font=ctk.CTkFont("Consolas", 12))
        self.enc_priv_txt.grid(row=4, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(left, text="Khóa công khai (B):").grid(row=5, column=0, columnspan=2, sticky="w", padx=15)
        self.enc_pub_txt = ctk.CTkTextbox(left, height=80, font=ctk.CTkFont("Consolas", 12))
        self.enc_pub_txt.grid(row=6, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        self.enc_keytime_var = ctk.StringVar()
        ctk.CTkLabel(left, textvariable=self.enc_keytime_var, text_color=MUTED_TEXT, font=ctk.CTkFont(size=11)).grid(row=7, column=0, columnspan=2, padx=15, pady=5)

        right = ctk.CTkFrame(parent, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(right, text="📝 Văn bản (Alice gửi):", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.enc_msg_txt = ctk.CTkTextbox(right, height=100, font=ctk.CTkFont("Consolas", 13), fg_color="#F8F9FA", border_width=1)
        self.enc_msg_txt.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self.enc_msg_txt.insert("0.0", "hello surface city")

        btn_frame = ctk.CTkFrame(right, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="w", pady=(0, 10))
        
        ctk.CTkButton(btn_frame, text="🔐 Mã hóa", command=lambda: self._run_in_thread(self.__enc_encrypt), fg_color="#0078D4").pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_frame, text="🔓 Giải mã", command=lambda: self._run_in_thread(self.__enc_decrypt), fg_color=SUCCESS_COLOR).pack(side="left")

        ctk.CTkLabel(right, text="📤 Kết quả Output:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=3, column=0, sticky="w", pady=(10, 5))
        self.enc_out_txt = ctk.CTkTextbox(right, font=ctk.CTkFont("Consolas", 13), fg_color="#1E1E1E", text_color="#00FF00")
        self.enc_out_txt.grid(row=4, column=0, sticky="nsew")

        self._enc_private_key     = None
        self._enc_public_key      = None
        self._enc_ciphertext      = None
        self._enc_plaintext_point = None
        self._enc_engine          = None

    # (Giữ nguyên toàn bộ Logic của Tab 2)
    def __enc_gen_keys(self):
        t0 = time.time()
        self._enc_curve  = EllipticCurve(self.enc_curve_var.get())
        self._enc_engine = ECElGamal(self._enc_curve)
        s, B = self._enc_engine.generate_keypair()
        self._enc_private_key = s
        self._enc_public_key  = B
        elapsed = time.time() - t0
        self.enc_priv_txt.delete("0.0", "end")
        self.enc_priv_txt.insert("end", str(s))
        self.enc_pub_txt.delete("0.0", "end")
        self.enc_pub_txt.insert("end", f"x = {B.x}\ny = {B.y}")
        self.enc_keytime_var.set(f"⏱ Tạo khóa: {elapsed*1000:.1f} ms")
        self.enc_out_txt.delete("0.0", "end")
        self.enc_out_txt.insert("end", f"✅ Đã tạo cặp khóa Bob ({self.enc_curve_var.get()}) trong {elapsed*1000:.1f} ms\n")

    def __enc_encrypt(self):
        if self._enc_public_key is None:
            messagebox.showwarning("Chưa tạo khóa", "Vui lòng tạo khóa Bob trước!")
            return
        msg = self.enc_msg_txt.get("0.0", "end").strip()
        if not msg: return
        t0 = time.time()
        (M1, M2), M = self._enc_engine.encrypt(msg, self._enc_public_key)
        self._enc_ciphertext      = (M1, M2)
        self._enc_plaintext_point = M
        elapsed = time.time() - t0
        self.enc_out_txt.delete("0.0", "end")
        self.enc_out_txt.insert("end", f"=== Mã hóa ElGamal ===\nĐiểm M nhúng:\n  x={M.x}\n  y={M.y}\n\nBản mã (M1, M2):\n  M1.x={M1.x}\n  M1.y={M1.y}\n  M2.x={M2.x}\n  M2.y={M2.y}\n\n⏱ Mã hóa trong {elapsed*1000:.1f} ms\n")

    def __enc_decrypt(self):
        if self._enc_ciphertext is None:
            messagebox.showwarning("Chưa mã hóa", "Vui lòng mã hóa văn bản trước!")
            return
        t0 = time.time()
        M_dec = self._enc_engine.decrypt(self._enc_ciphertext, self._enc_private_key)
        elapsed = time.time() - t0
        ok = self._enc_engine.points_equal(M_dec, self._enc_plaintext_point)
        status = "✅ Giải mã THÀNH CÔNG — điểm trùng khớp" if ok else "❌ Điểm không khớp"
        self.enc_out_txt.insert("end", f"\n=== Giải mã ===\nĐiểm M giải mã:\n  x={M_dec.x}\n  y={M_dec.y}\n\n{status}\nVăn bản gốc: \"{self.enc_msg_txt.get('0.0', 'end').strip()}\"\n⏱ Giải mã trong {elapsed*1000:.1f} ms\n")

    # ==================================================================
    # TAB 3 — AI IP Guardian
    # ==================================================================
    def _build_tab_guardian(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        top = ctk.CTkFrame(parent, fg_color="#F8F9FA", corner_radius=10)
        top.grid(row=0, column=0, sticky="ew", padx=15, pady=15)

        row1 = ctk.CTkFrame(top, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(row1, text="🤖 AI IP Guardian", font=ctk.CTkFont(size=18, weight="bold"), text_color="#1E293B").pack(side="left", padx=(0, 20))
        ctk.CTkLabel(row1, text="Nhập IP:").pack(side="left", padx=(0, 5))
        self.guard_ip_var = ctk.StringVar(value="192.168.1.100")
        ctk.CTkEntry(row1, textvariable=self.guard_ip_var, width=150, fg_color="#FFFFFF").pack(side="left", padx=(0, 20))

        ctk.CTkLabel(row1, text="Message:").pack(side="left", padx=(0, 5))
        self.guard_msg_var = ctk.StringVar(value="test_signature")
        ctk.CTkEntry(row1, textvariable=self.guard_msg_var, width=180, fg_color="#FFFFFF").pack(side="left", padx=(0, 20))

        self.guard_success_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(row1, text="Success", variable=self.guard_success_var).pack(side="left")

        row2 = ctk.CTkFrame(top, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkButton(row2, text="🔍 Kiểm tra", command=self._guard_check, fg_color="#0078D4").pack(side="left", padx=(0, 10))
        ctk.CTkButton(row2, text="⚡ Mô phỏng tấn công", command=lambda: self._run_in_thread(self.__guard_simulate), fg_color=DANGER_COLOR, hover_color="#b91c1c").pack(side="left", padx=(0, 10))
        ctk.CTkButton(row2, text="➕ Thêm Whitelist", command=self._guard_add_whitelist, fg_color=SUCCESS_COLOR, hover_color="#059669").pack(side="left", padx=(0, 10))
        ctk.CTkButton(row2, text="🔄 Reset IP", command=self._guard_reset, fg_color="#64748b", hover_color="#475569").pack(side="left", padx=(0, 10))
        ctk.CTkButton(row2, text="🚫 Xem Blocked", command=self._guard_show_blocked, fg_color="#7c2d12", hover_color="#451a03").pack(side="left")

        mid = ctk.CTkFrame(parent, fg_color="transparent")
        mid.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        mid.grid_columnconfigure(0, weight=1)
        mid.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(mid, text="📋 Nhật ký giám sát thời gian thực:", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.guard_log_txt = ctk.CTkTextbox(mid, font=ctk.CTkFont("Consolas", 13), fg_color="#1E1E1E", text_color="#00FF00")
        self.guard_log_txt.grid(row=1, column=0, sticky="nsew")

        self.guard_stats_var = ctk.StringVar(value="Sẵn sàng ghi nhận sự kiện...")
        ctk.CTkLabel(parent, textvariable=self.guard_stats_var, text_color=MUTED_TEXT, font=ctk.CTkFont(size=12)).grid(row=2, column=0, sticky="w", padx=15, pady=5)

    # (Giữ nguyên logic của AI Guardian)
    def _guard_log(self, msg):
        self.guard_log_txt.insert("end", msg + "\n")
        self.guard_log_txt.see("end")

    def _guard_check(self):
        ip     = self.guard_ip_var.get().strip()
        msg    = self.guard_msg_var.get().strip()
        ok     = self.guard_success_var.get()
        result = self.guardian.check(ip, success=ok, message=msg)
        icon = {"allow": "✅", "warn": "⚠️", "block": "🚫"}.get(result["status"], "❓")
        ts   = time.strftime("%H:%M:%S")
        self._guard_log(f"[{ts}] {icon} {result['status'].upper():6s} IP={ip:<18} Layer={result['layer']:<12} Score={result['score']:.3f}  {result['reason']}")
        stats = self.guardian.get_stats(ip)
        self.guard_stats_var.set(f"Thống kê {ip}: Total={stats['total']} | Fail={stats['fail']} | Rate={stats['fail_rate']:.0%} | Blocked={'YEP 🚫' if stats['is_blocked'] else 'No'}")

    def __guard_simulate(self):
        import random
        attacker = self.guard_ip_var.get().strip() or "10.0.0.99"
        self._guard_log(f"\n{'─'*60}\n⚡ Bắt đầu mô phỏng tấn công từ {attacker} ...")
        for i in range(70):
            ok = random.random() > 0.9
            result = self.guardian.check(attacker, success=ok, message=f"msg_{i}")
            ts   = time.strftime("%H:%M:%S")
            icon = {"allow": "✅", "warn": "⚠️", "block": "🚫"}.get(result["status"], "?")
            self._guard_log(f"[{ts}] req#{i+1:02d} {icon} {result['status']:6s} score={result['score']:.3f}  {result['reason']}")
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

    def _guard_show_blocked(self):
        blocked = self.guardian.get_blocked_list()
        self._guard_log(f"\n{'─'*60}\n🚫 Danh sách IP đang bị block ({len(blocked)} IP):")
        if not blocked: self._guard_log("  (trống)")
        else:
            for ip, info in blocked.items():
                t = time.strftime("%H:%M:%S", time.localtime(info["time"]))
                self._guard_log(f"  {ip:<20} Layer={info['layer']:<12} Lúc={t}  {info['reason']}")
        self._guard_log(f"{'─'*60}\n")