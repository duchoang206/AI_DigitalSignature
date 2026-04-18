# src/core/ecdsa.py
import secrets
from .elliptic_curve import EllipticCurve
from .point import Point, mod_inverse
from .utils import sha512_int

class ECDSA:
    def __init__(self, curve: EllipticCurve):
        self.curve = curve

    def generate_keypair(self):
        # Dùng secrets thay cho random
        d = secrets.randbelow(self.curve.n - 1) + 1
        Q = self.curve.scalar_mul(d, self.curve.G)
        return d, Q

    def sign(self, message: str, private_key: int):
        n = self.curve.n
        h = sha512_int(message) % n

        while True:
            # Dùng secrets để sinh k an toàn
            k = secrets.randbelow(n - 1) + 1
            R = self.curve.scalar_mul(k, self.curve.G)
            r = R.x % n
            if r == 0:
                continue
            k_inv = mod_inverse(k, n)
            s = k_inv * (h + private_key * r) % n
            if s == 0:
                continue
            return r, s

    def verify(self, message: str, signature: tuple, public_key: Point) -> bool:
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

class ECGDSA:
    def __init__(self, curve: EllipticCurve):
        self.curve = curve

    def generate_keypair(self):
        n = self.curve.n
        d = secrets.randbelow(n - 1) + 1
        d_inv = mod_inverse(d, n)
        Q = self.curve.scalar_mul(d_inv, self.curve.G)
        return d, Q

    def sign(self, message: str, private_key: int):
        n = self.curve.n
        h = sha512_int(message) % n

        while True:
            k = secrets.randbelow(n - 1) + 1
            R = self.curve.scalar_mul(k, self.curve.G)
            r = R.x % n
            if r == 0:
                continue
            s = (k * r - h) * private_key % n
            if s == 0:
                continue
            return r, s

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