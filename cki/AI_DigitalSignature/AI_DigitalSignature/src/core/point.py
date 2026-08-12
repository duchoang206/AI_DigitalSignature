# point.py — Phép toán điểm trên đường cong Elliptic (Fp)

class Point:
    """Đại diện cho một điểm trên đường cong Elliptic hoặc điểm vô cực O."""

    def __init__(self, x, y, infinity=False):
        self.x = x
        self.y = y
        self.infinity = infinity  # điểm trung hòa O

    @classmethod
    def infinity_point(cls):
        return cls(0, 0, infinity=True)

    def is_infinity(self):
        return self.infinity

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        if self.infinity and other.infinity:
            return True
        if self.infinity or other.infinity:
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        if self.infinity:
            return "Point(O)"
        return f"Point({self.x}, {self.y})"

    def __hash__(self):
        if self.infinity:
            return hash(("infinity",))
        return hash((self.x, self.y))


def mod_inverse(a: int, m: int) -> int:
    """Nghịch đảo modular bằng Extended Euclidean Algorithm."""
    if m == 1:
        return 0
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"Nghịch đảo modular không tồn tại: gcd({a}, {m}) = {g}")
    return x % m


def extended_gcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def point_add(P: Point, Q: Point, a: int, p: int) -> Point:
    """Cộng hai điểm P + Q trên đường cong E: y² = x³ + ax + b (mod p)."""
    if P.is_infinity():
        return Q
    if Q.is_infinity():
        return P

    if P.x == Q.x:
        # P = -Q → tổng là điểm vô cực
        if P.y != Q.y or P.y == 0:
            return Point.infinity_point()
        # P = Q → nhân đôi điểm
        lam = (3 * P.x * P.x + a) * mod_inverse(2 * P.y, p) % p
    else:
        lam = (Q.y - P.y) * mod_inverse(Q.x - P.x, p) % p

    x3 = (lam * lam - P.x - Q.x) % p
    y3 = (lam * (P.x - x3) - P.y) % p
    return Point(x3, y3)


def point_mul(k: int, P: Point, a: int, p: int) -> Point:
    """Nhân vô hướng k*P bằng phương pháp Double-and-Add (Left-to-Right)."""
    if k == 0:
        return Point.infinity_point()
    if k < 0:
        # k*P = (-k)*(-P)
        neg_P = Point(P.x, (-P.y) % p)
        return point_mul(-k, neg_P, a, p)

    result = Point.infinity_point()
    addend = Point(P.x, P.y)
    while k:
        if k & 1:
            result = point_add(result, addend, a, p)
        addend = point_add(addend, addend, a, p)
        k >>= 1
    return result
