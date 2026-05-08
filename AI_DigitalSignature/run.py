import sys
import os

# Đảm bảo Python nhận diện được thư mục src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import đúng tên class App từ main_app.py
from src.ui.main_app import App

if __name__ == "__main__":
    # Khởi tạo và chạy giao diện chính của hệ thống AI-ECDSA
    app = App()
    app.mainloop()