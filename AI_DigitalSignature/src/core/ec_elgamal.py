# ec_elgamal.py — EC ElGamal Encryption thuần Python

import random
from .elliptic_curve import EllipticCurve
from .point import Point
from .utils import text_to_point


class ECElGamal:
    """
    Mã hóa ElGamal trên đường cong Elliptic.
    
    Encrypt: (M1, M2) = (k·G, M + k·B)
    Decrypt: M = M2 - s·M1
    """
    def __init__(self, curve: EllipticCurve):
        self.curve = curve

    # ── Tạo cặp khóa ──────────────────────────────────
    def generate_keypair(self):
        """s: khóa riêng, B = s·G: khóa công khai."""
        s = random.randint(1, self.curve.n - 1)
        B = self.curve.scalar_mul(s, self.curve.G)
        return s, B

    # ── Mã hóa ────────────────────────────────────────
    def encrypt(self, message: str, public_key: Point):
        """
        Nhúng text → điểm M, chọn k ngẫu nhiên.
        Trả về (ciphertext_pair, k, M) để giải mã kiểm tra.
        """
        M = text_to_point(message, {
            "p": self.curve.p,
            "a": self.curve.a,
            "b": self.curve.b
        })
        k = random.randint(1, self.curve.n - 1)
        M1 = self.curve.scalar_mul(k, self.curve.G)       # k·G
        kB = self.curve.scalar_mul(k, public_key)          # k·B
        M2 = self.curve.add(M, kB)                         # M + k·B
        return (M1, M2), M

    # ── Giải mã ───────────────────────────────────────
    def decrypt(self, ciphertext: tuple, private_key: int) -> Point:
        """
        M = M2 - s·M1
        (trừ = cộng với điểm đối xứng)
        """
        M1, M2 = ciphertext
        sM1 = self.curve.scalar_mul(private_key, M1)      # s·M1
        neg_sM1 = Point(sM1.x, (-sM1.y) % self.curve.p)  # -(s·M1)
        M = self.curve.add(M2, neg_sM1)                    # M2 - s·M1
        return M

    # ── Tiện ích: so sánh điểm giải mã ───────────────
    def points_equal(self, P: Point, Q: Point) -> bool:
        return P.x == Q.x and P.y == Q.y
