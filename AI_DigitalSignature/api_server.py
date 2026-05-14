import sys
import os
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.elliptic_curve import EllipticCurve, get_available_curves
from src.core.ecdsa import ECDSA, ECGDSA
from src.core.ec_elgamal import ECElGamal
from src.core.point import Point
from src.ai.ip_guardian import IPGuardian

app = Flask(__name__)
CORS(app)

# Global instances (simplified for demo purposes)
guardian = IPGuardian()

@app.route('/api/sig/keys', methods=['POST'])
def sig_keys():
    data = request.json or {}
    curve_name = data.get('curve', 'secp112r1')
    algo_name = data.get('algo', 'ECDSA')
    
    t0 = time.time()
    curve = EllipticCurve(curve_name)
    eng = ECDSA(curve) if algo_name == "ECDSA" else ECGDSA(curve)
    d, Q = eng.generate_keypair()
    ms = (time.time() - t0) * 1000
    
    return jsonify({
        "success": True,
        "private_key": str(d),
        "public_key": {"x": str(Q.x), "y": str(Q.y)},
        "time_ms": round(ms, 1)
    })

@app.route('/api/sig/sign', methods=['POST'])
def sig_sign():
    data = request.json or {}
    msg = data.get('message', '')
    priv = int(data.get('private_key', '0'))
    curve_name = data.get('curve', 'secp112r1')
    algo_name = data.get('algo', 'ECDSA')
    
    if not msg or not priv:
        return jsonify({"success": False, "error": "Missing message or private key"})
        
    t0 = time.time()
    curve = EllipticCurve(curve_name)
    eng = ECDSA(curve) if algo_name == "ECDSA" else ECGDSA(curve)
    r, s = eng.sign(msg, priv)
    ms = (time.time() - t0) * 1000
    
    return jsonify({
        "success": True,
        "signature": {"r": str(r), "s": str(s)},
        "time_ms": round(ms, 1)
    })

@app.route('/api/sig/verify', methods=['POST'])
def sig_verify():
    data = request.json or {}
    msg = data.get('message', '')
    r = int(data.get('r', '0'))
    s = int(data.get('s', '0'))
    qx = int(data.get('qx', '0'))
    qy = int(data.get('qy', '0'))
    curve_name = data.get('curve', 'secp112r1')
    algo_name = data.get('algo', 'ECDSA')
    
    if not msg or not r or not s or not qx or not qy:
        return jsonify({"success": False, "error": "Missing parameters"})
        
    t0 = time.time()
    curve = EllipticCurve(curve_name)
    eng = ECDSA(curve) if algo_name == "ECDSA" else ECGDSA(curve)
    pub_key = Point(qx, qy, curve.a, curve.b)
    ok = eng.verify(msg, (r, s), pub_key)
    ms = (time.time() - t0) * 1000
    
    return jsonify({
        "success": True,
        "valid": ok,
        "time_ms": round(ms, 1)
    })

@app.route('/api/guard/check', methods=['POST'])
def guard_check():
    data = request.json or {}
    ip = data.get('ip', '192.168.1.100')
    msg = data.get('message', 'sign_request')
    success = data.get('success', True)
    
    res = guardian.check(ip, success=success, message=msg)
    stats = guardian.get_stats(ip)
    
    # Check if blocked in stats
    stats["is_blocked"] = res["status"] == "block"
    
    return jsonify({
        "success": True,
        "result": res,
        "stats": stats
    })

if __name__ == '__main__':
    print("Starting AI-ECDSA API Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
