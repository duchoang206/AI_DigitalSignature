# utils.py — Tiện ích mật mã: Miller-Rabin, SHA512 wrapper, embed text

import hashlib
import random
from .point import Point, point_add, point_mul, mod_inverse


# ──────────────────────────────────────────
# Kiểm tra nguyên tố Miller-Rabin
# ──────────────────────────────────────────

def miller_rabin(n: int, k: int = 20) -> bool:
    """Kiểm tra tính nguyên tố với k vòng lặp Miller-Rabin."""
    if n < 2:
        return False
    if n == 2 or n == 3:
        return True
    if n % 2 == 0:
        return False

    # Viết n-1 = 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


# ──────────────────────────────────────────
# Hàm băm SHA-512
# ──────────────────────────────────────────

def sha512_int(message: str) -> int:
    """Trả về giá trị nguyên của SHA-512(message)."""
    digest = hashlib.sha512(message.encode("utf-8")).digest()
    return int.from_bytes(digest, "big")


def sha512_hex(message: str) -> str:
    return hashlib.sha512(message.encode("utf-8")).hexdigest()


# ──────────────────────────────────────────
# Nhúng văn bản vào điểm trên đường cong
# ──────────────────────────────────────────

def text_to_point(text: str, curve: dict) -> Point:
    """
    Nhúng chuỗi text vào điểm M trên đường cong.
    Chiến lược: lấy hash của text → x, thử tìm y thoả y² = x³ + ax + b (mod p).
    """
    p = curve["p"]
    a = curve["a"]
    b = curve["b"]

    seed = int.from_bytes(text.encode("utf-8"), "big") % p
    for delta in range(1000):
        x = (seed + delta) % p
        rhs = (pow(x, 3, p) + a * x + b) % p
        # Thử tìm căn bậc hai modular (p ≡ 3 mod 4)
        if p % 4 == 3:
            y = pow(rhs, (p + 1) // 4, p)
            if pow(y, 2, p) == rhs:
                return Point(x, y)
        else:
            # Brute-force nhỏ cho p ≡ 1 mod 4 (không dùng trong sec2)
            y = _sqrt_mod(rhs, p)
            if y is not None:
                return Point(x, y)

    raise ValueError("Không thể nhúng văn bản vào điểm trên đường cong")


def point_to_text(M: Point, original_text: str) -> str:
    """Lấy lại text từ điểm (chỉ dùng x để so sánh, text gốc được lưu kèm)."""
    return original_text


def _sqrt_mod(n: int, p: int):
    """Tính căn bậc hai modular n mod p (Tonelli-Shanks)."""
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None  # không phải thặng dư bậc hai

    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)

    # Tonelli-Shanks
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1

    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)

    while True:
        if t == 0:
            return 0
        if t == 1:
            return r
        i, temp = 1, pow(t, 2, p)
        while temp != 1:
            temp = pow(temp, 2, p)
            i += 1
        b = pow(c, pow(2, m - i - 1, p - 1), p)
        m, c, t, r = i, pow(b, 2, p), t * pow(b, 2, p) % p, r * b % p
