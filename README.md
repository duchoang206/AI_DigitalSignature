<<<<<<< HEAD
# AI-ECDSA Digital Signature System 🔐
=======
# AI-ECDSA Digital Signature System 
>>>>>>> a12458c746945314a2c7d69ed1428894e55c8920

Hệ thống xác thực người dùng và chữ ký số dựa trên thuật toán ECDSA/ECGDSA, tích hợp lớp bảo vệ thông minh **AI IP Guardian** để ngăn chặn các hành vi tấn công mạng.

## 🌟 Tính năng chính

* **Mật mã học đường cong Elliptic (ECC):**
    * **ECDSA & ECGDSA**: Hỗ trợ ký và xác thực văn bản với độ bảo mật cao và kích thước khóa tối ưu.
    * **EC-ElGamal**: Hệ thống mã hóa bất đối xứng trên đường cong Elliptic.
    * **Đa dạng đường cong**: Hỗ trợ nhiều chuẩn đường cong như `secp112r1`, `secp160r1`, `secp256k1`,....
* **AI IP Guardian (Phòng vệ 3 lớp):**
    * **Lớp 1 (Hard Rules)**: Chặn IP ngay lập tức dựa trên các ngưỡng vật lý như giới hạn tốc độ (Rate-limit) và truy cập dồn dập (Burst requests).
    * **Lớp 2 (AI Layer)**: Sử dụng mô hình **Isolation Forest** để phát hiện hành vi bất thường dựa trên vector đặc trưng hành vi của IP.
    * **Lớp 3 (Whitelist)**: Quản lý danh sách các IP tin cậy để bỏ qua kiểm tra.
* **Giao diện trực quan**: Xây dựng bằng thư viện Tkinter, hỗ trợ quản lý khóa, thực hiện ký/mã hóa và theo dõi log bảo mật thời gian thực.

## 📂 Cấu trúc dự án

```text
AI_DigitalSignature/
├── run.py                # Điểm khởi chạy ứng dụng (Entry point)
├── requirements.txt      # Danh sách thư viện phụ thuộc
├── config/
│   └── whitelist.json    # Cấu hình danh sách IP tin cậy
├── src/
│   ├── core/             # Lõi mật mã (ECDSA, Elliptic Curve, EC-ElGamal)
│   ├── ai/               # Lõi AI (IP Guardian, Isolation Forest)
│   └── ui/               # Giao diện người dùng Tkinter
├── models/               # Lưu trữ mô hình AI đã huấn luyện
<<<<<<< HEAD
└── logs/                 # Nhật ký hoạt động và log bảo mật
=======
└── logs/                 # Nhật ký hoạt động và log bảo mật
>>>>>>> a12458c746945314a2c7d69ed1428894e55c8920
