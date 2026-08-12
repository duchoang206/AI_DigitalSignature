# elliptic_curve.py — Wrapper đường cong Elliptic

from .curves_db import get_curve, list_curves, list_ecdsa_curves
from .point import Point, point_mul, point_add, mod_inverse
from .utils import miller_rabin
import secrets


class EllipticCurve:
    """Đại diện cho đường cong Elliptic E: y² = x³ + ax + b (mod p)."""

    def __init__(self, name: str):
        params = get_curve(name)
        self.name = name
        self.bits = params["bits"]
        self.p = params["p"]
        self.a = params["a"]
        self.b = params["b"]
        self.G = Point(params["Gx"], params["Gy"])
        self.n = params["n"]
        self.h = params["h"]

    # ── Kiểm tra điểm thuộc đường cong ──
    def is_on_curve(self, P: Point) -> bool:
        if P.is_infinity():
            return True
        lhs = pow(P.y, 2, self.p)
        rhs = (pow(P.x, 3, self.p) + self.a * P.x + self.b) % self.p
        return lhs == rhs

    # ── Nhân vô hướng ──
    def scalar_mul(self, k: int, P: Point) -> Point:
        return point_mul(k, P, self.a, self.p)

    # ── Cộng điểm ──
    def add(self, P: Point, Q: Point) -> Point:
        return point_add(P, Q, self.a, self.p)

    # ── Validate tham số miền ──
    def validate(self) -> bool:
        discriminant = (4 * pow(self.a, 3) + 27 * pow(self.b, 2)) % self.p
        if discriminant == 0:
            return False
        if not self.is_on_curve(self.G):
            return False
        nG = self.scalar_mul(self.n, self.G)
        if not nG.is_infinity():
            return False
        return True

    def __repr__(self):
        return f"EllipticCurve({self.name}, {self.bits}bit)"


def get_available_curves(ecdsa_only: bool = False) -> list:
    """
    ecdsa_only=True  → chỉ trả về curves phù hợp ECDSA (h=1).
    ecdsa_only=False → tất cả curves (dùng cho ElGamal).
    """
    return list_ecdsa_curves() if ecdsa_only else list_curves()
