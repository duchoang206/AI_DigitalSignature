#!/usr/bin/env python3
"""
AI-ECDSA Digital Signature System
Entry point — chạy ứng dụng Tkinter
"""
import sys
import os

# Đảm bảo import đúng package
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.ui.main_app import run

if __name__ == "__main__":
    run()
