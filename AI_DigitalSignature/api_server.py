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
from src.ai.face_auth import BiometricAuth
from src.ai.chatbot import SecurityBot

app = Flask(__name__)
CORS(app)

# Global instances (simplified for demo purposes)
guardian = IPGuardian()
bot = SecurityBot()
# Initialize BiometricAuth with owner face
owner_face_path = os.path.join(os.path.dirname(__file__), "data", "owner_face.jpg")
biometric = BiometricAuth(owner_face_path)

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

@app.route('/api/chatbot/command', methods=['POST'])
def chatbot_command():
    data = request.json or {}
    user_input = data.get('text', '')
    cmd, response = bot.process_command(user_input)
    return jsonify({
        "success": True,
        "command": cmd,
        "response": response
    })

@app.route('/api/facenet/verify', methods=['POST'])
def facenet_verify():
    # In a real scenario, this would trigger the camera on the server side
    # or process a frames sent from client. For this local app demo,
    # we trigger the OpenCV window on the server machine.
    success = biometric.verify_owner()
    return jsonify({
        "success": True,
        "verified": success
    })

@app.route('/api/sig/stealth-sign', methods=['POST'])
def stealth_sign():
    data = request.json or {}
    msg = data.get('message', '')
    curve_name = data.get('curve', 'secp256k1')
    
    # Simulate: Retrieve encrypted private key from "secure storage"
    # and decrypt it into RAM (local variable)
    # In a real app, this would be retrieved from a DB or secure enclave
    dummy_private_key = 12345678901234567890 # Placeholder for demo
    
    t0 = time.time()
    try:
        curve = EllipticCurve(curve_name)
        eng = ECDSA(curve)
        r, s = eng.sign(msg, dummy_private_key)
        
        # Explicitly "clear" from RAM
        del dummy_private_key
        
        ms = (time.time() - t0) * 1000
        return jsonify({
            "success": True,
            "signature": {"r": str(r), "s": str(s)},
            "time_ms": round(ms, 1)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    print("Starting AI-ECDSA API Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
