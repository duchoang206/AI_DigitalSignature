from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import json
import os
from security.crypto_engine import CryptoEngine
from ai.face_engine import FaceEngine

app = Flask(__name__)
CORS(app)

# Configuration
DB_PATH = "AI_DigitalSignature/data/db.json"
FACE_DB_PATH = "AI_DigitalSignature/data/employee_faces"

# Initialize Engines
face_engine = FaceEngine(FACE_DB_PATH)
crypto_engine = CryptoEngine()

def load_db():
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    return {"employees": {}, "documents": []}

def save_db(db):
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=4)

@app.route('/api/enroll', methods=['POST'])
def enroll():
    data = request.json
    name = data.get('name')
    image_b64 = data.get('image').split(',')[1]
    
    # Decode image
    img_bytes = base64.b64decode(image_b64)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if face_engine.enroll_employee(img, name):
        # Generate ECDSA Keys
        priv, pub = crypto_engine.generate_key_pair()
        
        db = load_db()
        db["employees"][name] = {
            "public_key": pub,
            "private_key": priv # In a real app, this should be stored securely or handed to the user
        }
        save_db(db)
        
        return jsonify({"status": "success", "message": f"Đã đăng ký {name} thành công."})
    
    return jsonify({"status": "error", "message": "Không tìm thấy khuôn mặt."}), 400

@app.route('/api/identify', methods=['POST'])
def identify():
    data = request.json
    image_b64 = data.get('image').split(',')[1]
    
    img_bytes = base64.b64decode(image_b64)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    identity = face_engine.identify_face(img)
    if identity:
        return jsonify({"status": "success", "identity": identity})
    
    return jsonify({"status": "error", "message": "Không nhận diện được khuôn mặt."}), 404

@app.route('/api/sign-document', methods=['POST'])
def sign_document():
    data = request.json
    employee_name = data.get('employee_name')
    file_name = data.get('file_name')
    file_content_b64 = data.get('file_content') # Simulated content
    
    db = load_db()
    if employee_name not in db["employees"]:
        return jsonify({"status": "error", "message": "Nhân viên chưa đăng ký."}), 400
    
    employee = db["employees"][employee_name]
    file_bytes = base64.b64decode(file_content_b64) if file_content_b64 else b"dummy_content"
    
    # Create Signature
    signature = crypto_engine.sign_data(employee["private_key"], file_bytes)
    file_hash = crypto_engine.get_file_hash(file_bytes)
    
    doc_entry = {
        "id": str(len(db["documents"]) + 1),
        "name": file_name,
        "uploader": employee_name,
        "status": "Chờ duyệt",
        "signature": signature,
        "file_hash": file_hash,
        "isTampered": False
    }
    db["documents"].append(doc_entry)
    save_db(db)
    
    return jsonify({"status": "success", "document": doc_entry})

@app.route('/api/verify-and-approve', methods=['POST'])
def verify_and_approve():
    data = request.json
    doc_id = data.get('doc_id')
    manager_image_b64 = data.get('image').split(',')[1]
    
    db = load_db()
    doc = next((d for d in db["documents"] if d["id"] == doc_id), None)
    if not doc:
        return jsonify({"status": "error", "message": "Tài liệu không tồn tại."}), 404
    
    # 1. Authenticate Manager
    img_bytes = base64.b64decode(manager_image_b64)
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    identity = face_engine.identify_face(img)
    if not identity: # In demo, we might allow any known face as 'Manager' or check specific role
        return jsonify({"status": "error", "message": "Xác thực Sếp thất bại."}), 401
    
    # 2. Verify Document Integrity
    employee = db["employees"].get(doc["uploader"])
    if not employee:
        return jsonify({"status": "error", "message": "Thông tin nhân viên đã bị xóa."}), 400
    
    # Simulate integrity check: In real app, we'd hash the current file content
    # For demo, we check the isTampered flag set by our 'Hacker' button
    if doc["isTampered"]:
        return jsonify({"status": "tampered", "message": "CẢNH BÁO: Chữ ký không khớp với nội dung file!"})
    
    doc["status"] = "✅ Đã có hiệu lực"
    save_db(db)
    
    return jsonify({"status": "success", "message": "Phê duyệt thành công."})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
