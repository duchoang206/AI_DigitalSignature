# 🔐 AI-ECDSA Digital Signature System

> Đường cong Elliptic và ứng dụng trong Chữ ký số, tích hợp AI phát hiện IP nghi vấn  
> Đại học Quốc gia Hà Nội, 2026

---

## 📁 Cấu trúc dự án

```
AI_DigitalSignature/
│
├── run.py                        ← Khởi chạy ứng dụng
├── requirements.txt              ← Thư viện cần cài
├── README.md
│
├── src/
│   ├── core/                     ← Thuật toán mật mã 
│   │   ├── point.py              ← Phép toán điểm trên đường cong Elliptic
│   │   ├── elliptic_curve.py     ← Wrapper EllipticCurve, kiểm tra tham số miền
│   │   ├── utils.py              ← Miller-Rabin, SHA-512, nhúng text vào điểm
│   │   ├── ecdsa.py              ← ECDSA + ECGDSA (dùng secrets CSPRNG)
│   │   ├── ec_elgamal.py         ← EC ElGamal Encryption/Decryption
│   │   ├── curves_db.py          ← 11 đường cong SEC2 (đã xác minh toàn bộ)
│   │   └── __init__.py
│   │
│   ├── ai/                       ← Module AI bảo mật IP
│   │   ├── ip_guardian.py        ← Isolation Forest + Hard Rules + Whitelist
│   │   └── __init__.py
│   │
│   └── ui/
│       ├── main_app.py           ← Giao diện Tkinter (3 tab)
│       └── __init__.py
│
├── tests/
│   ├── test_ecdsa.py             ← Unit test ECDSA / ECGDSA / ElGamal + benchmark
│   └── test_ip_guardian.py       ← Unit test AI IP Guardian
│
├── models/
│   └── ip_guardian.pkl           ← Model Isolation Forest (tự sinh khi chạy lần đầu)
├── logs/
│   └── ip_guardian.log           ← Log sự kiện block/warn/allow
└── config/
    └── whitelist.json            ← Danh sách IP tin cậy
```

---

## ⚙️ Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|---|---|
| Python | 3.9+ |
| numpy | 1.24.0+ |
| scikit-learn | 1.3.0+ |
| tkinter | Có sẵn trong Python chuẩn |

> **Hệ điều hành:** Windows 10/11, macOS 12+, Ubuntu 20.04+

---

## 🚀 Hướng dẫn cài đặt và chạy

### Bước 1 — Giải nén dự án

```bash
# Giải nén file zip vào thư mục mong muốn
unzip AI_DigitalSignature.zip
cd AI_DigitalSignature
```

### Bước 2 — Tạo môi trường ảo (khuyến nghị)

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt (Windows)
venv\Scripts\activate

# Kích hoạt (macOS / Linux)
source venv/bin/activate
```

### Bước 3 — Cài thư viện

```bash
pip install -r requirements.txt
```

> Nếu bạn dùng Python hệ thống (không dùng venv):
> ```bash
> pip install numpy scikit-learn
> ```

### Bước 4 — Chạy ứng dụng

```bash
python run.py
```

Lần đầu chạy, hệ thống sẽ tự động:
- Huấn luyện model Isolation Forest (~3 giây)
- Lưu model vào `models/ip_guardian.pkl`
- Tạo file `config/whitelist.json` với IP mặc định `127.0.0.1`, `::1`

---

## 🧪 Chạy Unit Tests

```bash
# Test thuật toán mật mã (ECDSA, ECGDSA, ElGamal)
python tests/test_ecdsa.py

# Test AI IP Guardian
python tests/test_ip_guardian.py
```

> **Lưu ý:** `test_ip_guardian.py` có hàm `test_normal_traffic()` được comment sẵn vì chạy chậm (~10 giây). Bỏ comment nếu muốn test đầy đủ.

---

## 🖥️ Hướng dẫn sử dụng giao diện

### Tab 1 — Chữ ký số (ECDSA / ECGDSA)

| Bước | Thao tác |
|------|----------|
| 1 | Chọn **đường cong** từ danh sách (secp112r1 → secp521r1) |
| 2 | Chọn **thuật toán**: ECDSA hoặc ECGDSA |
| 3 | Nhấn **🔑 Tạo cặp khóa** — kết quả hiện trong ô Private Key và Public Key |
| 4 | Nhập **văn bản cần ký** vào ô Message |
| 5 | Nhấn **✍️ Ký số** → nhận được chữ ký (r, s) |
| 6 | Nhấn **✅ Xác thực** → kết quả HỢP LỆ / KHÔNG HỢP LỆ |
| 7 | Nhấn **🗑 Xóa** để bắt đầu lại |

### Tab 2 — Mã hóa EC ElGamal

| Bước | Thao tác |
|------|----------|
| 1 | Chọn **đường cong** (hỗ trợ tất cả 11 curves) |
| 2 | Nhấn **🔑 Tạo khóa Bob** |
| 3 | Nhập **văn bản Alice muốn gửi** |
| 4 | Nhấn **🔐 Mã hóa** → nhận bản mã (M1, M2) |
| 5 | Nhấn **🔓 Giải mã** → xác nhận điểm trùng khớp |

### Tab 3 — AI IP Guardian

| Nút | Chức năng |
|-----|-----------|
| 🔍 Kiểm tra | Kiểm tra 1 request từ IP nhập sẵn |
| ⚡ Mô phỏng tấn công | Gửi 70 request liên tiếp, 90% thất bại → quan sát AI block |
| ➕ Thêm Whitelist | Thêm IP vào danh sách tin cậy (không bao giờ bị block) |
| 🔄 Reset IP | Xóa lịch sử và trạng thái block của IP |
| 🚫 Xem Blocked | Hiển thị toàn bộ danh sách IP đang bị block |

---

## 🔒 Thuật toán & Đường cong hỗ trợ

### Đường cong SEC2

| Curve | Bits | Dùng cho |
|-------|------|----------|
| secp112r1 | 112 | ECDSA, ECGDSA, ElGamal |
| secp128r1 | 128 | ECDSA, ECGDSA, ElGamal |
| secp160r1 | 160 | ECDSA, ECGDSA, ElGamal |
| secp160r2 | 160 | ECDSA, ECGDSA, ElGamal |
| secp192r1 | 192 | ECDSA, ECGDSA, ElGamal |
| secp224r1 | 224 | ECDSA, ECGDSA, ElGamal |
| secp256r1 | 256 | ECDSA, ECGDSA, ElGamal |
| secp384r1 | 384 | ECDSA, ECGDSA, ElGamal |
| secp521r1 | 521 | ECDSA, ECGDSA, ElGamal |
| secp112r2 | 112 | ElGamal (h=4, không dùng cho ECDSA) |
| secp128r2 | 128 | ElGamal (h=4, không dùng cho ECDSA) |

### AI IP Guardian — 3 lớp bảo vệ

```
Request đến
     │
     ▼
[L3] IP có trong Whitelist? ──→ YES → ALLOW (bypass tất cả)
     │ NO
     ▼
[L3] IP đang trong Blocked Registry? ──→ YES → BLOCK (instant, không tính lại)
     │ NO
     ▼
[L1] Hard Rules (tức thì):
     ├─ Rate > 60 req/60s    → BLOCK
     ├─ Fail rate > 80%      → BLOCK
     └─ Burst > 10 req/10s  → BLOCK
     │ OK
     ▼
[L2] Isolation Forest (7 features):
     ├─ Score ≥ 0.55  → WARN
     └─ Score < 0.55  → ALLOW
```

**7 features AI:**
```
request_rate    — số request trong 60 giây
fail_rate       — tỉ lệ verify thất bại
unique_messages — số message khác nhau
hour_of_day     — giờ trong ngày (0-23)
is_new_ip       — IP lần đầu xuất hiện (0/1)
time_since_last — khoảng cách giữa 2 request (giây)
burst_flag      — ≥10 request trong 10 giây (0/1)
```

---

## 📊 Hiệu năng thực đo (máy tham chiếu)

| Curve | Tạo khóa | Ký | Xác thực |
|-------|----------|----|---------|
| secp112r1 | ~8ms | ~5ms | ~10ms |
| secp128r1 | ~11ms | ~7ms | ~15ms |
| secp160r1 | ~18ms | ~12ms | ~25ms |
| secp192r1 | ~32ms | ~22ms | ~45ms |
| secp256r1 | ~63ms | ~42ms | ~85ms |
| secp384r1 | ~147ms | ~98ms | ~198ms |
| secp521r1 | ~283ms | ~188ms | ~380ms |

> Số liệu chi tiết hơn xem tại Bảng 4 & 5 trong báo cáo khóa luận.

---

## 🔧 Xử lý lỗi thường gặp

**`ModuleNotFoundError: No module named 'tkinter'`**
```bash
# Ubuntu / Debian
sudo apt-get install python3-tk

# macOS (Homebrew)
brew install python-tk
```

**`ModuleNotFoundError: No module named 'sklearn'`**
```bash
pip install scikit-learn
```

**Cửa sổ không hiển thị (WSL/headless server)**
```bash
# Cài X server (VcXsrv) trên Windows và set DISPLAY
export DISPLAY=:0
python run.py
```

**Model huấn luyện lại mỗi lần chạy**
```bash
# Đảm bảo thư mục models/ tồn tại và có quyền ghi
mkdir -p models
```

---

## 📚 Người hướng dẫn 
- Senior Security SurfaceCity Việt Nam 
