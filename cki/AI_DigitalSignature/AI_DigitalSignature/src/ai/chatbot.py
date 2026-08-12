class SecurityBot:
    def __init__(self):
        self.bot_name = "AI Copilot"

    def process_command(self, user_input):
        """
        Process user input and return a tuple of (command, response).
        command can be:
        - "command_sign": trigger the sign functionality
        - "command_verify": trigger the verify functionality
        - "command_keygen": trigger keygen functionality
        - "chat": general chat response
        """
        text = user_input.lower().strip()
        
        if "pipeline_config.json" in text or "ký file" in text or "ký tệp" in text or "sign file" in text or "sign document" in text:
            if "pipeline_config.json" in text:
                return "command_open_sign_doc", "Tôi sẽ mở hộp thoại chọn file cấu hình pipeline_config.json cho bạn."
            return "command_open_sign_doc", "Tôi sẽ mở hộp thoại chọn tài liệu để ký. Vui lòng chọn file cần ký."
        
        elif "ký" in text or "sign" in text:
            return "command_open_sign_doc", "Tôi sẽ mở hộp thoại chọn tài liệu để ký. Vui lòng chọn file cần ký."
        
        elif "xác thực" in text or "verify" in text or "kiểm tra" in text:
            return "command_verify", "Chế độ xác thực chữ ký. Vui lòng chọn tài liệu, file .sig và Public Key của người gửi."
            
        elif "tạo khóa" in text or "keygen" in text:
            return "command_keygen", "Bạn muốn tạo cặp khóa mới. Vui lòng chọn đường cong và thuật toán."
            
        elif "chào" in text or "hello" in text or "hi " in text:
            return "chat", "Chào bạn, hệ thống chữ ký số đã sẵn sàng. Bạn muốn ký tài liệu hay xác thực file hôm nay?"
            
        elif "clear" in text or "xóa" in text:
            return "command_clear", "Đã dọn dẹp lịch sử trò chuyện."
            
        else:
            return "chat", "Xin lỗi, tôi chưa hiểu rõ lệnh của bạn. Bạn có thể yêu cầu 'ký file', 'xác thực tài liệu', hoặc 'tạo khóa mới'."
