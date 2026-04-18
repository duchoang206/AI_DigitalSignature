#!/usr/bin/env python3
"""Unit tests cho AI IP Guardian"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.ai.ip_guardian import IPGuardian

PASS = "✅ PASS"
FAIL = "❌ FAIL"


def test_whitelist():
    print("\n── Test L3 Whitelist ──")
    g = IPGuardian()
    g.add_to_whitelist("10.0.0.1")
    r = g.check("10.0.0.1", True, "msg")
    ok = r["status"] == "allow" and r["layer"] == "whitelist"
    print(f"  Whitelist bypass: {PASS if ok else FAIL}")
    assert ok


def test_rate_limit():
    print("\n── Test L1 Rate Limit ──")
    g = IPGuardian()
    ip = "203.0.113.50"
    blocked = False
    for i in range(70):
        r = g.check(ip, True, f"msg{i}")
        if r["status"] == "block" and r["layer"] == "hard_rule":
            blocked = True
            print(f"  Block sau {i+1} req: {PASS}")
            break
    print(f"  {'Block không xảy ra:' if not blocked else ''}", end="")
    if not blocked:
        print(FAIL)
    assert blocked


def test_fail_rate():
    print("\n── Test L1 Fail Rate ──")
    g = IPGuardian()
    ip = "198.51.100.1"
    blocked = False
    for i in range(30):
        r = g.check(ip, success=False, message=f"bad{i}")
        if r["status"] == "block" and r["layer"] == "hard_rule":
            blocked = True
            print(f"  Block fail_rate sau {i+1} req: {PASS}")
            break
    if not blocked:
        print(f"  Không block: {FAIL}")
    assert blocked


def test_burst():
    print("\n── Test L1 Burst ──")
    g = IPGuardian()
    ip = "10.10.10.10"
    blocked = False
    # Gửi BURST_LIMIT req liên tiếp rất nhanh
    for i in range(15):
        r = g.check(ip, True, f"burst{i}")
        if r["status"] == "block":
            blocked = True
            print(f"  Block burst sau {i+1} req: {PASS}")
            break
    if not blocked:
        print(f"  Không block burst: {FAIL}")
    assert blocked


def test_normal_traffic():
    print("\n── Test Normal Traffic (allow) ──")
    g = IPGuardian()
    ip = "192.168.0.5"
    results = []
    # Gửi chậm (1 req / 1.2s) → không trigger burst, rate thấp
    for i in range(8):
        r = g.check(ip, True, f"normal_msg_{i}")
        results.append(r["status"])
        time.sleep(1.2)
    blocked_or_warned = [s for s in results if s != "allow"]
    ok = len(blocked_or_warned) == 0
    print(f"  {len(results)} req bình thường → all allow: {PASS if ok else FAIL}")
    if not ok:
        print(f"    Trạng thái: {results}")
    assert ok


def test_reset():
    print("\n── Test Reset IP ──")
    g = IPGuardian()
    ip = "172.16.0.99"
    for i in range(5):
        g.check(ip, False, "bad")
    g.reset_ip(ip)
    stats = g.get_stats(ip)
    ok = stats["total"] == 0
    print(f"  Reset xóa thống kê: {PASS if ok else FAIL}")
    assert ok


def test_ai_layer():
    print("\n── Test L2 AI Layer (simulated anomaly) ──")
    g = IPGuardian()
    ip = "99.99.99.99"
    warned_or_blocked = False
    # Mô phỏng bất thường: fail_rate cao + is_new_ip
    for i in range(20):
        r = g.check(ip, success=False, message="hack")
        if r["status"] in ("warn", "block"):
            warned_or_blocked = True
            print(f"  AI/Rule phát hiện bất thường sau {i+1} req ({r['layer']}): {PASS}")
            break
    if not warned_or_blocked:
        print(f"  Không phát hiện: {FAIL}")
    assert warned_or_blocked


if __name__ == "__main__":
    print("\n🤖  AI IP Guardian — Unit Tests\n")
    test_whitelist()
    test_rate_limit()
    test_fail_rate()
    test_burst()
    test_reset()
    test_ai_layer()
    # test_normal_traffic()  # chậm (~10s), bỏ chú thích để test đầy đủ
    print("\n✅  Tất cả test AI Guardian đã qua!")
