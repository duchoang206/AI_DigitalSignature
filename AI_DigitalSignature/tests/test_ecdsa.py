#!/usr/bin/env python3/
"""Unit tests cho ECDSA, ECGDSA, EC ElGamal"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.elliptic_curve import EllipticCurve
from src.core.ecdsa import ECDSA, ECGDSA
from src.core.ec_elgamal import ECElGamal

PASS = "✅ PASS"
FAIL = "❌ FAIL"
SEP  = "─" * 55


def test_ecdsa(curve_name="secp112r1"):
    print(f"\n{'═'*55}")
    print(f"  ECDSA — {curve_name}")
    print('═'*55)
    curve  = EllipticCurve(curve_name)
    engine = ECDSA(curve)

    # 1. Tạo khóa
    t0 = time.time()
    d, Q = engine.generate_keypair()
    t_key = (time.time() - t0) * 1000
    assert curve.is_on_curve(Q), "Khóa công khai không thuộc đường cong"
    print(f"  Tạo khóa:  {t_key:.1f} ms   {PASS}")

    # 2. Ký
    msg = "hello world — AI-ECDSA test"
    t0 = time.time()
    r, s = engine.sign(msg, d)
    t_sign = (time.time() - t0) * 1000
    print(f"  Ký:        {t_sign:.1f} ms   {PASS}")

    # 3. Xác thực đúng
    t0 = time.time()
    ok = engine.verify(msg, (r, s), Q)
    t_verify = (time.time() - t0) * 1000
    res = PASS if ok else FAIL
    print(f"  Xác thực:  {t_verify:.1f} ms   {res}")

    # 4. Xác thực sai (message thay đổi)
    ok_tampered = engine.verify("tampered message", (r, s), Q)
    res2 = PASS if not ok_tampered else FAIL
    print(f"  Phát hiện giả mạo:      {res2}")

    assert ok and not ok_tampered
    return t_key, t_sign, t_verify


def test_ecgdsa(curve_name="secp112r1"):
    print(f"\n{'═'*55}")
    print(f"  ECGDSA — {curve_name}")
    print('═'*55)
    curve  = EllipticCurve(curve_name)
    engine = ECGDSA(curve)

    t0 = time.time()
    d, Q = engine.generate_keypair()
    t_key = (time.time() - t0) * 1000
    print(f"  Tạo khóa:  {t_key:.1f} ms   {PASS}")

    msg = "hello world — ECGDSA test"
    t0 = time.time()
    r, s = engine.sign(msg, d)
    t_sign = (time.time() - t0) * 1000
    print(f"  Ký:        {t_sign:.1f} ms   {PASS}")

    t0 = time.time()
    ok = engine.verify(msg, (r, s), Q)
    t_verify = (time.time() - t0) * 1000
    res = PASS if ok else FAIL
    print(f"  Xác thực:  {t_verify:.1f} ms   {res}")

    ok_tampered = engine.verify("tampered", (r, s), Q)
    res2 = PASS if not ok_tampered else FAIL
    print(f"  Phát hiện giả mạo:      {res2}")

    assert ok and not ok_tampered
    return t_key, t_sign, t_verify


def test_elgamal(curve_name="secp112r1"):
    print(f"\n{'═'*55}")
    print(f"  EC ElGamal — {curve_name}")
    print('═'*55)
    curve  = EllipticCurve(curve_name)
    engine = ECElGamal(curve)

    t0 = time.time()
    s, B = engine.generate_keypair()
    t_key = (time.time() - t0) * 1000
    print(f"  Tạo khóa:  {t_key:.1f} ms   {PASS}")

    msg = "hello world"
    t0 = time.time()
    (M1, M2), M_orig = engine.encrypt(msg, B)
    t_enc = (time.time() - t0) * 1000
    print(f"  Mã hóa:    {t_enc:.1f} ms   {PASS}")

    t0 = time.time()
    M_dec = engine.decrypt((M1, M2), s)
    t_dec = (time.time() - t0) * 1000
    ok = engine.points_equal(M_dec, M_orig)
    res = PASS if ok else FAIL
    print(f"  Giải mã:   {t_dec:.1f} ms   {res}")
    assert ok
    return t_key, t_enc, t_dec


def benchmark():
    """So sánh thời gian trên nhiều đường cong."""
    curves = ["secp112r1", "secp128r1", "secp160r1", "secp192r1", "secp256r1"]
    print(f"\n{'═'*70}")
    print("  BENCHMARK (ms)")
    print(f"  {'Curve':<14} {'ECDSA-Key':>10} {'ECDSA-Sign':>11} {'ECDSA-Verify':>13} "
          f"{'ECGDSA-Key':>11} {'ECGDSA-Sign':>12}")
    print('─'*70)
    for c in curves:
        try:
            ek, es, ev = test_ecdsa.__wrapped__(c) if hasattr(test_ecdsa, "__wrapped__") \
                         else _bench_ecdsa(c)
            gk, gs, gv = _bench_ecgdsa(c)
            print(f"  {c:<14} {ek:>10.1f} {es:>11.1f} {ev:>13.1f} {gk:>11.1f} {gs:>12.1f}")
        except Exception as e:
            print(f"  {c:<14} ERROR: {e}")
    print('═'*70)


def _bench_ecdsa(cname):
    curve = EllipticCurve(cname)
    e = ECDSA(curve)
    t0 = time.time(); d, Q = e.generate_keypair(); tk = (time.time()-t0)*1000
    t0 = time.time(); sig = e.sign("bench", d);     ts = (time.time()-t0)*1000
    t0 = time.time(); e.verify("bench", sig, Q);    tv = (time.time()-t0)*1000
    return tk, ts, tv


def _bench_ecgdsa(cname):
    curve = EllipticCurve(cname)
    e = ECGDSA(curve)
    t0 = time.time(); d, Q = e.generate_keypair(); tk = (time.time()-t0)*1000
    t0 = time.time(); sig = e.sign("bench", d);    ts = (time.time()-t0)*1000
    t0 = time.time(); e.verify("bench", sig, Q);   tv = (time.time()-t0)*1000
    return tk, ts, tv


if __name__ == "__main__":
    print("\n🔐  AI-ECDSA — Unit Tests\n")
    test_ecdsa("secp112r1")
    test_ecgdsa("secp112r1")
    test_elgamal("secp112r1")
    benchmark()
    print(f"\n{'═'*55}")
    print("  Tất cả test đã qua ✅")
    print('═'*55)
