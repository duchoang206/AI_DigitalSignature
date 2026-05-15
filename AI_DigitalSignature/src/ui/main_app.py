# main_app.py — AI-ECDSA Cyber-security Dashboard (Futuristic UI)

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.core.elliptic_curve import EllipticCurve, get_available_curves
from src.core.ecdsa import ECDSA, ECGDSA
from src.core.ec_elgamal import ECElGamal
from src.ai.face_auth import BiometricAuth
from src.ai.chatbot import SecurityBot

# ══════════════════════════════════════════════════════════════════
#  DESIGN TOKENS  — Futuristic Monochromatic Dark Indigo & Electric Cyan
# ══════════════════════════════════════════════════════════════════
VOID_BG      = "#050814"
GLASS_BG     = "#0B1120"
GLASS_L2     = "#111827"
CYAN         = "#00E5FF"
CYAN_DIM     = "#008B99"
CYAN_DARK    = "#003344"
INDIGO       = "#1E1B4B"
TEXT_WHITE   = "#FFFFFF"
TEXT_CYAN    = "#A5F3FC"
TEXT_MUTED   = "#6B7280"
ERROR_RED    = "#FF003C"
SUCCESS_GN   = "#00FF66"

FONT_LOGO    = ("Segoe UI Light", 16)
FONT_NAV     = ("Consolas", 10)
FONT_TITLE   = ("Segoe UI", 11, "bold")
FONT_LABEL   = ("Consolas", 9)
FONT_BODY    = ("Consolas", 9)
FONT_MONO    = ("Consolas", 9)
FONT_BTN     = ("Consolas", 10, "bold")

def _btn(parent, text, cmd, bg=CYAN_DARK, fg=CYAN, outline=CYAN, pad_x=14, pad_y=6):
    f = tk.Frame(parent, bg=outline, padx=1, pady=1)
    b = tk.Button(f, text=text, command=cmd,
                  bg=bg, fg=fg, activebackground=CYAN,
                  activeforeground=VOID_BG, relief="flat",
                  cursor="hand2", font=FONT_BTN,
                  padx=pad_x, pady=pad_y, bd=0)
    b.pack(fill="both", expand=True)
    b.bind("<Enter>", lambda e: b.config(bg=CYAN_DIM, fg=TEXT_WHITE))
    b.bind("<Leave>", lambda e: b.config(bg=bg, fg=fg))
    return f

def _entry_txt(parent, h=4, w=40):
    t = scrolledtext.ScrolledText(
        parent, height=h, width=w,
        bg=VOID_BG, fg=TEXT_CYAN, insertbackground=CYAN,
        relief="flat", bd=0, font=FONT_MONO, wrap=tk.WORD,
        highlightthickness=1, highlightbackground=CYAN_DARK,
        highlightcolor=CYAN
    )
    return t

def _hollow_btn(parent, text, cmd):
    return _btn(parent, text, cmd, bg=VOID_BG, fg=TEXT_CYAN, outline=CYAN_DIM, pad_x=10, pad_y=4)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SECURITY PROTOCOL | MICROSOFT SURFACECITY")
        self.configure(bg=VOID_BG)
        self.geometry("1500x900")
        self.minsize(1300, 750)
        self.resizable(True, True)

        self.face_net = BiometricAuth(os.path.join(os.path.dirname(__file__), "../../data/owner_face.jpg"))
        self.chatbot = SecurityBot()
        self._temp_priv_key = None
        self._sig_key_meta = None

        self._build_header()
        self._build_navbar()
        self._build_body()
        self._build_statusbar()

    def _build_header(self):
        hdr = tk.Frame(self, bg=VOID_BG, height=60)
        hdr.pack(fill="x", pady=(10, 0))
        hdr.pack_propagate(False)

        inner = tk.Frame(hdr, bg=VOID_BG)
        inner.pack(fill="both", expand=True, padx=40)

        # Logo abstract
        logo_f = tk.Frame(inner, bg=VOID_BG)
        logo_f.pack(side="left", pady=10)
        
        c = tk.Canvas(logo_f, width=24, height=24, bg=VOID_BG, highlightthickness=0)
        c.create_rectangle(2, 2, 10, 10, fill=CYAN, outline="")
        c.create_rectangle(14, 2, 22, 10, fill=TEXT_WHITE, outline="")
        c.create_rectangle(2, 14, 10, 22, fill=TEXT_CYAN, outline="")
        c.create_rectangle(14, 14, 22, 22, fill=CYAN_DIM, outline="")
        c.pack(side="left", padx=(0, 10))

        tk.Label(logo_f, text="MICROSOFT", bg=VOID_BG, fg=TEXT_WHITE, font=FONT_LOGO).pack(side="left")
        tk.Label(logo_f, text="SURFACECITY", bg=VOID_BG, fg=CYAN, font=("Segoe UI", 16, "bold")).pack(side="left", padx=(5, 0))
        tk.Label(logo_f, text=" // CENTRAL COMMAND", bg=VOID_BG, fg=CYAN_DARK, font=("Consolas", 12)).pack(side="left", padx=(10, 0))

        sys_status = tk.Frame(inner, bg=VOID_BG)
        sys_status.pack(side="right", pady=15)
        tk.Label(sys_status, text="SYS.STATUS: ", bg=VOID_BG, fg=TEXT_MUTED, font=FONT_MONO).pack(side="left")
        tk.Label(sys_status, text="OPTIMAL", bg=VOID_BG, fg=CYAN, font=("Consolas", 10, "bold")).pack(side="left")
        
        tk.Frame(self, bg=CYAN_DARK, height=1).pack(fill="x", padx=40, pady=(0, 10))

    def _build_navbar(self):
        nav = tk.Frame(self, bg=VOID_BG, height=40)
        nav.pack(fill="x", padx=40)
        nav.pack_propagate(False)

        tabs_info = [
            ("HOME_INTERFACE", 0),
            ("DIGITAL_SIGNATURE", 1),
            ("EC_ENCRYPTION", 2),
        ]
        self._nav_btns = []
        
        for text, idx in tabs_info:
            f = tk.Frame(nav, bg=VOID_BG, padx=1, pady=1)
            f.pack(side="left", padx=(0, 20))
            
            b = tk.Label(f, text=f"[{text}]", bg=VOID_BG, fg=TEXT_MUTED,
                         font=FONT_NAV, padx=10, pady=5, cursor="hand2")
            b.pack(fill="both", expand=True)
            
            b.bind("<Button-1>", lambda e, i=idx: self._nb.select(i))
            b.bind("<Enter>", lambda e, w=b, i=idx: w.config(fg=CYAN if self._nb.index("current") != i else TEXT_WHITE))
            b.bind("<Leave>", lambda e, w=b, i=idx: w.config(fg=TEXT_MUTED if self._nb.index("current") != i else TEXT_WHITE))
            
            self._nav_btns.append((b, f, idx))

    def _build_body(self):
        body = tk.Frame(self, bg=VOID_BG)
        body.pack(fill="both", expand=True, padx=40, pady=(10, 20))
        
        left_panel = tk.Frame(body, bg=VOID_BG)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 20))
        
        right_panel = tk.Frame(body, bg=GLASS_L2, width=350, highlightthickness=1, highlightbackground=CYAN_DARK)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)
        self._build_chatbot(right_panel)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Cyber.TNotebook", background=VOID_BG, borderwidth=0)
        style.layout("Cyber.TNotebook.Tab", [])

        self._nb = ttk.Notebook(left_panel, style="Cyber.TNotebook")
        self._nb.pack(fill="both", expand=True)

        self.tab_home  = tk.Frame(self._nb, bg=GLASS_BG)
        self.tab_sig   = tk.Frame(self._nb, bg=GLASS_BG)
        self.tab_enc   = tk.Frame(self._nb, bg=GLASS_BG)

        self._nb.add(self.tab_home,  text="Home")
        self._nb.add(self.tab_sig,   text="Sig")
        self._nb.add(self.tab_enc,   text="Enc")

        self._build_tab_home(self.tab_home)
        self._build_tab_sig(self.tab_sig)
        self._build_tab_enc(self.tab_enc)

        self._nb.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self._nb.select(1) # Default to signature tab
        
    def _on_tab_changed(self, event):
        current = self._nb.index("current")
        for btn, frm, idx in self._nav_btns:
            if idx == current:
                btn.config(fg=TEXT_WHITE)
                frm.config(bg=CYAN)
            else:
                btn.config(fg=TEXT_MUTED)
                frm.config(bg=VOID_BG)

    def _build_tab_home(self, parent):
        tk.Label(parent, text="SYSTEM ONLINE", bg=GLASS_BG, fg=CYAN, font=("Consolas", 40, "bold")).pack(expand=True)
        tk.Label(parent, text="Select a module from the navigation bar to proceed.", bg=GLASS_BG, fg=TEXT_CYAN, font=FONT_NAV).pack()

    # ══════════════════════════════════════════════════
    #  TAB 1 — Chữ ký số (3 CỘT LIỀN KỀ NHAU)
    # ══════════════════════════════════════════════════
    def _build_tab_sig(self, parent):
        container = tk.Frame(parent, bg=VOID_BG, highlightthickness=1, highlightbackground=CYAN_DARK)
        container.pack(fill="both", expand=True)

        # Cột 1: KEY GENERATION
        c1 = tk.Frame(container, bg=GLASS_L2)
        c1.pack(side="left", fill="both", expand=True)
        self._build_sig_keygen(c1)

        tk.Frame(container, bg=CYAN, width=1).pack(side="left", fill="y")

        # Cột 2: SIGN DOCUMENT
        c2 = tk.Frame(container, bg=GLASS_L2)
        c2.pack(side="left", fill="both", expand=True)
        self._build_sig_sign(c2)

        tk.Frame(container, bg=CYAN, width=1).pack(side="left", fill="y")

        # Cột 3: VERIFY SIGNATURE
        c3 = tk.Frame(container, bg=GLASS_L2)
        c3.pack(side="left", fill="both", expand=True)
        self._build_sig_verify(c3)

        self._sig_private_key = None
        self._sig_public_key = None
        self._sig_engine = None

    def _build_sig_keygen(self, parent):
        self._sec_title(parent, "PHASE 01: KEY GENERATION")
        body = tk.Frame(parent, bg=GLASS_L2)
        body.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._lbl(body, "SELECT ELLIPTIC CURVE:").pack(anchor="w", pady=(0, 5))
        self.sig_curve_var = tk.StringVar(value="secp256k1")
        cb = ttk.Combobox(body, textvariable=self.sig_curve_var, values=get_available_curves(ecdsa_only=True), state="readonly", font=FONT_BODY)
        cb.pack(fill="x", pady=(0, 15))
        
        self._lbl(body, "SELECT ALGORITHM:").pack(anchor="w", pady=(0, 5))
        self.sig_algo_var = tk.StringVar(value="ECDSA")
        rf = tk.Frame(body, bg=GLASS_L2)
        rf.pack(anchor="w", pady=(0, 25))
        for algo in ["ECDSA", "ECGDSA"]:
            tk.Radiobutton(rf, text=algo, variable=self.sig_algo_var, value=algo, bg=GLASS_L2, fg=TEXT_CYAN, selectcolor=VOID_BG, activebackground=GLASS_L2, activeforeground=CYAN, font=FONT_BODY).pack(side="left", padx=(0, 15))
                           
        _btn(body, ">> INITIALIZE KEYPAIR", self._sig_gen).pack(fill="x", pady=(0, 20))
        
        self.sig_time_var = tk.StringVar(value="IDLE")
        tk.Label(body, textvariable=self.sig_time_var, bg=GLASS_L2, fg=SUCCESS_GN, font=FONT_MONO).pack(anchor="w", pady=(0, 15))

        self._lbl(body, "PRIVATE KEY (DO NOT SHARE):").pack(anchor="w", pady=(0, 5))
        self.sig_priv_txt = _entry_txt(body, h=3)
        self.sig_priv_txt.pack(fill="x", pady=(0, 10))
        _hollow_btn(body, "[ EXPORT PRIVATE .JSON ]", lambda: self._sig_save_key('private')).pack(anchor="e", pady=(0, 20))
        
        self._lbl(body, "PUBLIC KEY (SHAREABLE):").pack(anchor="w", pady=(0, 5))
        self.sig_pub_txt = _entry_txt(body, h=4)
        self.sig_pub_txt.pack(fill="x", pady=(0, 10))
        _hollow_btn(body, "[ EXPORT PUBLIC .JSON ]", lambda: self._sig_save_key('public')).pack(anchor="e")

    def _build_sig_sign(self, parent):
        self._sec_title(parent, "PHASE 02: SIGN DOCUMENT")
        body = tk.Frame(parent, bg=GLASS_L2)
        body.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._lbl(body, "TARGET DOCUMENT (PDF/DOCX/TXT):").pack(anchor="w", pady=(0, 5))
        self.sign_doc_var = tk.StringVar()
        self.sign_doc_label = self._drop_zone(body, self.sign_doc_var, "CLICK TO BROWSE DOCUMENT", filetypes=[("All Files", "*.*")])
        
        self._lbl(body, "YOUR PRIVATE KEY (.JSON):").pack(anchor="w", pady=(15, 5))
        self.sign_key_var = tk.StringVar()
        self.sign_key_label = self._drop_zone(body, self.sign_key_var, "CLICK TO BROWSE PRIVATE KEY", filetypes=[("JSON Files", "*.json")])
        
        tk.Frame(body, bg=GLASS_L2, height=20).pack()
        _btn(body, ">> EXECUTE SIGNATURE", self._sig_sign).pack(fill="x", pady=(10, 20))
        
        self._lbl(body, "SYSTEM OUTPUT:").pack(anchor="w", pady=(0, 5))
        self.sign_out_txt = _entry_txt(body, h=10)
        self.sign_out_txt.pack(fill="both", expand=True)

    def _build_sig_verify(self, parent):
        self._sec_title(parent, "PHASE 03: VERIFY INTEGRITY")
        body = tk.Frame(parent, bg=GLASS_L2)
        body.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._lbl(body, "ORIGINAL DOCUMENT:").pack(anchor="w", pady=(0, 5))
        self.verify_doc_var = tk.StringVar()
        self._drop_zone(body, self.verify_doc_var, "BROWSE RECEIVED DOCUMENT", filetypes=[("All Files", "*.*")])
        
        self._lbl(body, "SIGNATURE FILE (.SIG):").pack(anchor="w", pady=(15, 5))
        self.verify_sig_var = tk.StringVar()
        self._drop_zone(body, self.verify_sig_var, "BROWSE SIGNATURE FILE", filetypes=[("Signature Files", "*.sig")])
        
        self._lbl(body, "SENDER'S PUBLIC KEY (.JSON):").pack(anchor="w", pady=(15, 5))
        self.verify_key_var = tk.StringVar()
        self._drop_zone(body, self.verify_key_var, "BROWSE PUBLIC KEY", filetypes=[("JSON Files", "*.json")])
        
        tk.Frame(body, bg=GLASS_L2, height=10).pack()
        _btn(body, ">> RUN VERIFICATION", self._sig_verify).pack(fill="x", pady=(10, 20))
        
        self._lbl(body, "VERDICT:").pack(anchor="w", pady=(0, 5))
        self.verify_out_txt = _entry_txt(body, h=6)
        self.verify_out_txt.pack(fill="both", expand=True)

    def _drop_zone(self, parent, var, placeholder, filetypes):
        f = tk.Frame(parent, bg=INDIGO, highlightthickness=1, highlightbackground=CYAN_DARK, cursor="hand2")
        f.pack(fill="x")
        
        lbl = tk.Label(f, text=placeholder, bg=INDIGO, fg=CYAN, font=FONT_MONO, pady=12)
        lbl.pack(fill="both", expand=True)
        
        def _browse(e):
            path = filedialog.askopenfilename(filetypes=filetypes)
            if path:
                var.set(path)
                filename = os.path.basename(path)
                lbl.config(text=f"FILE LOADED: {filename}", fg=TEXT_WHITE)
                
        f.bind("<Button-1>", _browse)
        lbl.bind("<Button-1>", _browse)
        
        # Hover effect
        def _on_enter(e): f.config(bg=CYAN_DARK); lbl.config(bg=CYAN_DARK)
        def _on_leave(e): f.config(bg=INDIGO); lbl.config(bg=INDIGO)
        f.bind("<Enter>", _on_enter)
        f.bind("<Leave>", _on_leave)
        lbl.bind("<Enter>", _on_enter)
        lbl.bind("<Leave>", _on_leave)
        return lbl

    def _sec_title(self, parent, text):
        hdr = tk.Frame(parent, bg=CYAN_DARK)
        hdr.pack(fill="x")
        tk.Label(hdr, text=text, bg=CYAN_DARK, fg=TEXT_WHITE, font=FONT_BTN, pady=8, padx=15).pack(anchor="w")
        tk.Frame(parent, bg=CYAN, height=1).pack(fill="x")

    def _lbl(self, parent, text):
        return tk.Label(parent, text=text, bg=GLASS_L2, fg=TEXT_MUTED, font=FONT_LABEL)

    # --------------------------------------------------
    # SIG LOGIC (Untouched, converted formatting)
    # --------------------------------------------------
    def _sig_gen(self):     self._run(self.__sig_gen)
    def _sig_sign(self):    self._run(self.__sig_sign)
    def _sig_verify(self):  self._run(self.__sig_verify)

    def __sig_gen(self):
        self._set_status("GENERATING KEYPAIR...")
        t0 = time.time()
        curve = EllipticCurve(self.sig_curve_var.get())
        algo  = self.sig_algo_var.get()
        eng   = ECDSA(curve) if algo == "ECDSA" else ECGDSA(curve)
        self._sig_engine = eng
        d, Q  = eng.generate_keypair()
        self._sig_private_key = d
        self._sig_public_key  = Q
        self._sig_key_meta = {"curve": self.sig_curve_var.get(), "algo": self.sig_algo_var.get()}
        ms = (time.time() - t0) * 1000

        self.sig_priv_txt.delete("1.0", tk.END)
        self.sig_priv_txt.insert(tk.END, str(d))
        self.sig_pub_txt.delete("1.0", tk.END)
        self.sig_pub_txt.insert(tk.END, f"x = {Q.x}\ny = {Q.y}")
        self.sig_time_var.set(f"SUCCESS: {ms:.1f}ms")
        self._set_status("KEYPAIR GENERATED")

    def _sig_save_key(self, key_type):
        if not self._sig_private_key or not self._sig_public_key:
            messagebox.showwarning("SYS.WARN", "Initialize keys first."); return
        title = "Export Private Key" if key_type == 'private' else "Export Public Key"
        f = filedialog.asksaveasfilename(title=title, defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if f:
            try:
                data = {
                    "curve": self.sig_curve_var.get(),
                    "algo": self.sig_algo_var.get(),
                    "type": key_type
                }
                if key_type == 'private':
                    data["private_key"] = self._sig_private_key
                else:
                    data["public_key"] = {"x": self._sig_public_key.x, "y": self._sig_public_key.y}
                with open(f, 'w', encoding='utf-8') as file:
                    json.dump(data, file)
                messagebox.showinfo("SYS.INFO", f"Key exported to:\n{f}")
            except Exception as e:
                messagebox.showerror("SYS.ERR", f"Export failed: {e}")

    def __sig_sign(self):
        doc_path = self.sign_doc_var.get()
        key_path = self.sign_key_var.get()
        
        if not doc_path or not os.path.exists(doc_path):
            messagebox.showwarning("SYS.WARN", "Valid document required."); return
        
        temp_priv_key = None
        temp_meta = None
        key_data = None
        file_private_used = False

        if key_path and os.path.exists(key_path):
            try:
                with open(key_path, 'r', encoding='utf-8') as f:
                    key_data = json.load(f)
                if key_data.get("type") != "private":
                    messagebox.showerror("SYS.ERR", "Invalid Private Key format."); return
                temp_priv_key = key_data["private_key"]
                temp_meta = {"curve": key_data["curve"], "algo": key_data["algo"]}
                file_private_used = True
            except Exception as e:
                messagebox.showerror("SYS.ERR", f"Unable to load private key: {e}"); return
        elif self._sig_private_key is not None and self._sig_key_meta is not None:
            temp_priv_key = self._sig_private_key
            temp_meta = self._sig_key_meta
        else:
            messagebox.showwarning("SYS.WARN", "Private key required. Vui lòng tạo khóa hoặc tải private key lên."); return

        curve = EllipticCurve(temp_meta["curve"])
        algo = temp_meta["algo"]
        eng = ECDSA(curve) if algo == "ECDSA" else ECGDSA(curve)

        self._set_status("AWAITING BIOMETRIC AUTH...")
        self._append_chat("System", "Đang kích hoạt module FaceNet. Vui lòng nhìn thẳng vào camera.")
        is_owner = self.face_net.verify_owner()

        if not is_owner:
            self._append_chat("System", "CẢNH BÁO: Khuôn mặt không khớp hoặc đã hủy. Khóa bị đóng băng.")
            self._set_status("AUTH FAILED")
            messagebox.showerror("SECURITY ALERT", "Xác thực khuôn mặt thất bại!")
            temp_priv_key = None
            if key_data is not None: del key_data
            return

        self._append_chat("System", "Xác thực khuôn mặt thành công. Khóa Private Key được giải mã trong bộ nhớ tạm và tiến hành ký...")

        try:
            with open(doc_path, 'rb') as f:
                msg_hex = f.read().hex()

            self._set_status("SIGNING DOCUMENT...")
            t0 = time.time()
            r, s = eng.sign(msg_hex, temp_priv_key)
            ms = (time.time() - t0) * 1000

            sig_file = doc_path + ".sig"
            with open(sig_file, 'w', encoding='utf-8') as f:
                f.write(f"""{algo}
{curve.name}
{r}
{s}""")

            self.sign_out_txt.delete("1.0", tk.END)
            self._out(self.sign_out_txt, f""">> SIGNATURE GENERATED SUCCESSFULLY
>> LATENCY: {ms:.1f} ms
>> OUTPUT TARGET:
{sig_file}

[!] Distribute both original file and .sig file.""")
            self._set_status(f"SIGNATURE SUCCESS ({ms:.1f}ms)")

            # Clear temporary private key from memory
            temp_priv_key = None
            if key_data is not None:
                del key_data
            if file_private_used:
                self.sign_key_var.set("")
                if hasattr(self, 'sign_key_label'):
                    self.sign_key_label.config(text="CLICK TO BROWSE PRIVATE KEY", fg=CYAN)

        except Exception as e:
            messagebox.showerror("SYS.ERR", f"Sign failed: {e}")
            temp_priv_key = None
            if key_data is not None:
                del key_data

    def __sig_verify(self):
        doc_path = self.verify_doc_var.get()
        sig_path = self.verify_sig_var.get()
        key_path = self.verify_key_var.get()
        
        if not doc_path or not os.path.exists(doc_path): return messagebox.showwarning("SYS.WARN", "Document missing")
        if not sig_path or not os.path.exists(sig_path): return messagebox.showwarning("SYS.WARN", "Signature missing")
        if not key_path or not os.path.exists(key_path): return messagebox.showwarning("SYS.WARN", "Public Key missing")
            
        try:
            with open(key_path, 'r', encoding='utf-8') as f:
                key_data = json.load(f)
            if key_data.get("type") != "public": return messagebox.showerror("SYS.ERR", "Invalid Public Key")
                
            with open(sig_path, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split("\n")
                if len(lines) != 4: return messagebox.showerror("SYS.ERR", "Corrupted Signature format")
                algo, curve_name, r_str, s_str = lines
                
            if key_data["curve"] != curve_name or key_data["algo"] != algo: return messagebox.showerror("SYS.ERR", "Algorithm/Curve mismatch")
                
            curve = EllipticCurve(curve_name)
            eng = ECDSA(curve) if algo == "ECDSA" else ECGDSA(curve)
            
            from src.core.elliptic_curve import Point
            pub_key = Point(key_data["public_key"]["x"], key_data["public_key"]["y"])
            signature = (int(r_str), int(s_str))
            
            with open(doc_path, 'rb') as f:
                msg_hex = f.read().hex()
                
            self._set_status("VERIFYING...")
            t0 = time.time()
            ok = eng.verify(msg_hex, signature, pub_key)
            ms = (time.time() - t0) * 1000
            
            self.verify_out_txt.delete("1.0", tk.END)
            if ok:
                self._out(self.verify_out_txt, f"""[ SUCCESS ] INTEGRITY VERIFIED
>> Document matches signature cryptographically.
>> Sender identity confirmed.
>> Latency: {ms:.1f} ms""")
                self.verify_out_txt.config(fg=SUCCESS_GN)
                self._set_status("VERIFICATION: VALID")
            else:
                self._out(self.verify_out_txt, f"""[ FAILED ] INTEGRITY BREACHED
>> Document has been altered or signature is forged.
>> DO NOT TRUST THIS FILE.
>> Latency: {ms:.1f} ms""")
                self.verify_out_txt.config(fg=ERROR_RED)
                self._set_status("VERIFICATION: INVALID")
                
        except Exception as e:
            messagebox.showerror("SYS.ERR", f"Verification error: {e}")

    # ══════════════════════════════════════════════════
    #  TAB 2 — EC ElGamal
    # ══════════════════════════════════════════════════
    def _build_tab_enc(self, parent):
        container = tk.Frame(parent, bg=VOID_BG, highlightthickness=1, highlightbackground=CYAN_DARK)
        container.pack(fill="both", expand=True)

        left = tk.Frame(container, bg=GLASS_L2, width=400)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self._sec_title(left, "ENCRYPTION CONFIG")

        body = tk.Frame(left, bg=GLASS_L2)
        body.pack(fill="both", padx=20, pady=20)

        self._lbl(body, "ELLIPTIC CURVE:").pack(anchor="w", pady=(0, 5))
        self.enc_curve_var = tk.StringVar(value="secp112r1")
        ttk.Combobox(body, textvariable=self.enc_curve_var, values=get_available_curves(ecdsa_only=False), state="readonly", font=FONT_LABEL).pack(fill="x", pady=(0, 15))

        _btn(body, ">> GENERATE BOB'S KEY", lambda: self._run(self.__enc_gen)).pack(fill="x", pady=(0, 20))

        self._lbl(body, "PRIVATE KEY (s):").pack(anchor="w", pady=(0, 5))
        self.enc_priv_txt = _entry_txt(body, h=3)
        self.enc_priv_txt.pack(fill="x", pady=(0, 15))

        self._lbl(body, "PUBLIC KEY (B):").pack(anchor="w", pady=(0, 5))
        self.enc_pub_txt = _entry_txt(body, h=4)
        self.enc_pub_txt.pack(fill="x", pady=(0, 15))

        self.enc_time_var = tk.StringVar()
        tk.Label(body, textvariable=self.enc_time_var, bg=GLASS_L2, fg=CYAN, font=FONT_MONO).pack(anchor="w")

        tk.Frame(container, bg=CYAN, width=1).pack(side="left", fill="y")

        right = tk.Frame(container, bg=GLASS_BG)
        right.pack(side="left", fill="both", expand=True)

        self._sec_title(right, "TERMINAL: SECURE MESSAGE")
        
        r_body = tk.Frame(right, bg=GLASS_BG)
        r_body.pack(fill="both", expand=True, padx=20, pady=20)

        self._lbl(r_body, "PLAINTEXT MESSAGE:").pack(anchor="w", pady=(0, 5))
        self.enc_msg_txt = _entry_txt(r_body, h=5)
        self.enc_msg_txt.pack(fill="x", pady=(0, 15))
        self.enc_msg_txt.insert("1.0", "hello world")

        btn_row = tk.Frame(r_body, bg=GLASS_BG)
        btn_row.pack(fill="x", pady=(0, 20))
        _btn(btn_row, "[ ENCRYPT ]", lambda: self._run(self.__enc_encrypt)).pack(side="left", fill="x", expand=True, padx=(0, 10))
        _hollow_btn(btn_row, "[ DECRYPT ]", lambda: self._run(self.__enc_decrypt)).pack(side="left", fill="x", expand=True)

        self._lbl(r_body, "CIPHERTEXT / OUTPUT:").pack(anchor="w", pady=(0, 5))
        self.enc_out_txt = _entry_txt(r_body, h=10)
        self.enc_out_txt.pack(fill="both", expand=True)

        self._enc_priv = self._enc_pub = None
        self._enc_ct = self._enc_M = self._enc_eng = None

    def __enc_gen(self):
        self._set_status("GENERATING BOB'S KEY...")
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
        self.enc_time_var.set(f"LATENCY: {ms:.1f} ms")
        self.enc_out_txt.delete("1.0", tk.END)
        self._out(self.enc_out_txt, f""">> KEYPAIR INITIALIZED ({self.enc_curve_var.get()})

s = {s}
B.x = {B.x}
B.y = {B.y}
""")
        self._set_status("BOB'S KEY READY")

    def __enc_encrypt(self):
        if not self._enc_pub: return messagebox.showwarning("SYS.WARN", "Initialize Bob's key first.")
        msg = self.enc_msg_txt.get("1.0", tk.END).strip()
        if not msg: return
        self._set_status("ENCRYPTING...")
        t0 = time.time()
        (M1, M2), M = self._enc_eng.encrypt(msg, self._enc_pub)
        self._enc_ct, self._enc_M = (M1, M2), M
        ms = (time.time() - t0) * 1000
        self.enc_out_txt.delete("1.0", tk.END)
        self._out(self.enc_out_txt, f"""{'='*50}
[ EC ELGAMAL ENCRYPTION ]
{'='*50}
PLAINTEXT : '{msg}'

EMBEDDED POINT M:
  x = {M.x}
  y = {M.y}

CIPHERTEXT (M1, M2):
  M1.x = {M1.x}
  M1.y = {M1.y}
  M2.x = {M2.x}
  M2.y = {M2.y}

>> LATENCY: {ms:.1f} ms
""")
        self._set_status("ENCRYPTION COMPLETE")

    def __enc_decrypt(self):
        if not self._enc_ct: return messagebox.showwarning("SYS.WARN", "No ciphertext available.")
        self._set_status("DECRYPTING...")
        t0 = time.time()
        Md = self._enc_eng.decrypt(self._enc_ct, self._enc_priv)
        ms = (time.time() - t0) * 1000
        ok = self._enc_eng.points_equal(Md, self._enc_M)
        self.enc_out_txt.insert(tk.END, f"""
{'-'*50}
[ DECRYPTION ]
{'-'*50}
RECOVERED POINT:
  x = {Md.x}
  y = {Md.y}

>> {'[ SUCCESS ] INTEGRITY MATCH' if ok else '[ FAILED ] CORRUPTION DETECTED'}
>> RECOVERED PLAINTEXT: '{self.enc_msg_txt.get('1.0', tk.END).strip()}'
>> LATENCY: {ms:.1f} ms
""")
        self.enc_out_txt.see(tk.END)
        self._set_status("DECRYPTION COMPLETE")

    def _build_chatbot(self, parent):
        self._sec_title(parent, "AI COPILOT")
        chat_body = tk.Frame(parent, bg=GLASS_L2)
        chat_body.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.chat_history = scrolledtext.ScrolledText(
            chat_body, bg=VOID_BG, fg=TEXT_CYAN, insertbackground=CYAN,
            relief="flat", bd=0, font=FONT_BODY, wrap=tk.WORD,
            highlightthickness=1, highlightbackground=CYAN_DARK,
            highlightcolor=CYAN
        )
        self.chat_history.pack(fill="both", expand=True, pady=(0, 15))
        self.chat_history.config(state=tk.DISABLED)
        
        self.chat_entry = tk.Entry(
            chat_body, bg=VOID_BG, fg=TEXT_WHITE, insertbackground=CYAN,
            relief="flat", font=FONT_BODY, highlightthickness=1, 
            highlightbackground=CYAN_DARK, highlightcolor=CYAN
        )
        self.chat_entry.pack(fill="x", ipady=8, pady=(0, 10))
        self.chat_entry.bind("<Return>", self._handle_chat)
        
        _btn(chat_body, "SEND COMMAND", self._handle_chat).pack(fill="x")
        
        self._append_chat(self.chatbot.bot_name, "Chào bạn, hệ thống chữ ký số đã sẵn sàng. Bạn muốn ký tài liệu hay xác thực file hôm nay?")

    def _append_chat(self, sender, message):
        self.chat_history.config(state=tk.NORMAL)
        if sender == "You":
            self.chat_history.insert(tk.END, f"[{sender}]\n{message}\n\n", "user")
            self.chat_history.tag_config("user", foreground=TEXT_WHITE)
        else:
            self.chat_history.insert(tk.END, f"[{sender}]\n{message}\n\n", "bot")
            self.chat_history.tag_config("bot", foreground=CYAN)
        self.chat_history.see(tk.END)
        self.chat_history.config(state=tk.DISABLED)

    def _handle_chat(self, event=None):
        msg = self.chat_entry.get().strip()
        if not msg: return
        self.chat_entry.delete(0, tk.END)
        self._append_chat("You", msg)
        
        cmd, response = self.chatbot.process_command(msg)
        self._append_chat(self.chatbot.bot_name, response)
        
        if cmd in ("command_sign", "command_open_sign_doc"):
            self._nb.select(1) # Select Signature tab
            if self._browse_sign_document():
                self._run(self.__sig_sign)
            else:
                self._append_chat("System", "Hủy thao tác mở file ký. Nếu bạn muốn tiếp tục, hãy gõ lại lệnh ký file.")
        elif cmd == "command_verify":
            self._nb.select(1) # Select Signature tab
        elif cmd == "command_keygen":
            self._nb.select(1) # Select Signature tab
        elif cmd == "command_clear":
            self.chat_history.config(state=tk.NORMAL)
            self.chat_history.delete("1.0", tk.END)
            self.chat_history.config(state=tk.DISABLED)

    def _out(self, widget, text):
        widget.insert(tk.END, text + "\n")
        widget.see(tk.END)

    def _browse_sign_document(self):
        path = filedialog.askopenfilename(title="Select document to sign", filetypes=[("All Files", "*.*")])
        if not path:
            return False
        self.sign_doc_var.set(path)
        if hasattr(self, 'sign_doc_label'):
            self.sign_doc_label.config(text=f"FILE LOADED: {os.path.basename(path)}", fg=TEXT_WHITE)
        self._append_chat("System", f"File đã chọn: {os.path.basename(path)}")
        return True

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=VOID_BG, height=30)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)
        
        tk.Frame(bar, bg=CYAN_DARK, height=1).pack(fill="x", padx=40)
        
        self._status_var = tk.StringVar(value="SYSTEM READY")
        tk.Label(bar, textvariable=self._status_var,
                 bg=VOID_BG, fg=TEXT_CYAN, font=FONT_MONO,
                 anchor="w", padx=40, pady=5).pack(fill="both", expand=True)

    def _set_status(self, msg):
        self._status_var.set(f"> {msg}")

    def _run(self, fn, *a):
        threading.Thread(target=fn, args=a, daemon=True).start()

def run():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    run()
