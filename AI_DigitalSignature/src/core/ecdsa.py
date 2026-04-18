# ecdsa.py — ECDSA + ECGDSA thuần Python

import random
from .elliptic_curve import EllipticCurve
from .point import Point, point_mul, mod_inverse
from .utils import sha512_int


# ══════════════════════════════════════════════════════
# ECDSA — Elliptic Curve Digital Signature Algorithm
# ══════════════════════════════════════════════════════

class ECDSA:
    def __init__(self, curve: EllipticCurve):
        self.curve = curve

    # ── Tạo cặp khóa ──────────────────────────────────
    def generate_keypair(self):
        """
        d  : khóa riêng (private key) — số ngẫu nhiên ∈ [1, n-1]
        Q  : khóa công khai (public key) — Q = d·G
        """
        d = random.randint(1, self.curve.n - 1)
        Q = self.curve.scalar_mul(d, self.curve.G)
        return d, Q

    # ── Ký số ─────────────────────────────────────────
    def sign(self, message: str, private_key: int):
        """
        Tạo chữ ký số (r, s) cho message.
        s = k⁻¹(h + d·r) mod n
        """
        n = self.curve.n
        h = sha512_int(message) % n

        while True:
            k = random.randint(1, n - 1)
            R = self.curve.scalar_mul(k, self.curve.G)
            r = R.x % n
            if r == 0:
                continue
            k_inv = mod_inverse(k, n)
            s = k_inv * (h + private_key * r) % n
            if s == 0:
                continue
            return r, s

    # ── Xác thực chữ ký ───────────────────────────────
    def verify(self, message: str, signature: tuple, public_key: Point) -> bool:
        """
        Xác thực chữ ký (r, s).
        X = u1·G + u2·Q,  v = X.x mod n,  chấp nhận nếu v == r
        """
        r, s = signature
        n = self.curve.n

        if not (1 <= r <= n - 1 and 1 <= s <= n - 1):
            return False

        h = sha512_int(message) % n
        w = mod_inverse(s, n)
        u1 = h * w % n
        u2 = r * w % n

        G = self.curve.G
        X = self.curve.add(
            self.curve.scalar_mul(u1, G),
            self.curve.scalar_mul(u2, public_key)
        )

        if X.is_infinity():
            return False

        v = X.x % n
        return v == r


# ══════════════════════════════════════════════════════
# ECGDSA — German Digital Signature Algorithm on EC
# ══════════════════════════════════════════════════════

class ECGDSA:
    """
    Biến thể ECDSA của Đức: phép tính nghịch đảo thực hiện khi tạo khóa,
    không phải khi ký → tiết kiệm thời gian khi ký nhiều văn bản.
    s = (k·r – h)·d mod n
    """
    def __init__(self, curve: EllipticCurve):
        self.curve = curve

    # ── Tạo cặp khóa ──────────────────────────────────
    def generate_keypair(self):
        """
        d   : khóa riêng
        d'  : d⁻¹ mod n (tính sẵn tại đây)
        Q   : d'·G  (khóa công khai)
        Trả về (d, Q)
        """
        n = self.curve.n
        d = random.randint(1, n - 1)
        d_inv = mod_inverse(d, n)
        Q = self.curve.scalar_mul(d_inv, self.curve.G)
        return d, Q

    # ── Ký số ─────────────────────────────────────────
    def sign(self, message: str, private_key: int):
        n = self.curve.n
        h = sha512_int(message) % n

        while True:
            k = random.randint(1, n - 1)
            R = self.curve.scalar_mul(k, self.curve.G)
            r = R.x % n
            if r == 0:
                continue
            s = (k * r - h) * private_key % n
            if s == 0:
                continue
            return r, s

    # ── Xác thực chữ ký ───────────────────────────────
    def verify(self, message: str, signature: tuple, public_key: Point) -> bool:
        r, s = signature
        n = self.curve.n

        if not (1 <= r <= n - 1 and 1 <= s <= n - 1):
            return False

        h = sha512_int(message) % n
        w = mod_inverse(r, n)
        t1 = w * h % n
        t2 = w * s % n

        X = self.curve.add(
            self.curve.scalar_mul(t1, self.curve.G),
            self.curve.scalar_mul(t2, public_key)
        )

        if X.is_infinity():
            return False

        v = X.x % n
        return v == r
