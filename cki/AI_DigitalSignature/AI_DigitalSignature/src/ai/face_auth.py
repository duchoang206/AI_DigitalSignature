import cv2
import os

class BiometricAuth:
    def __init__(self, reference_image_path):
        self.reference_image = reference_image_path
        self.model_name = "Facenet" # Use FaceNet model via deepface
        
        # Check if reference image exists
        if not os.path.exists(self.reference_image):
            print(f"[!] Warning: Reference image not found at {self.reference_image}")

    def verify_owner(self):
        """Turn on camera and verify face"""
        # Lazy import deepface so it doesn't slow down initial app startup
        try:
            from deepface import DeepFace
        except ImportError:
            print("[!] DeepFace is not installed. Returning False.")
            return False

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[!] Error: Could not open camera. Hardware might be in use by another app.")
            return False
            
        print("Đang bật camera xác thực...")
        
        verified = False
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            # Add some instructions on the frame
            display_frame = frame.copy()
            cv2.putText(display_frame, "Nhan 'v' de xac thuc / 'q' de huy", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.imshow('FaceNet Authentication', display_frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('v'):
                try:
                    print("Đang so sánh khuôn mặt...")
                    # Compare directly the camera frame with reference image
                    result = DeepFace.verify(frame, 
                                             self.reference_image, 
                                             model_name=self.model_name,
                                             enforce_detection=False)
                    verified = result["verified"]
                    if verified:
                        print("Xác thực thành công!")
                    else:
                        print("Khuôn mặt không khớp!")
                except Exception as e:
                    print("Lỗi nhận diện:", e)
                break
                
            elif key == ord('q'):
                print("Đã hủy xác thực khuôn mặt.")
                break
                
        cap.release()
        cv2.destroyAllWindows()
        return verified
