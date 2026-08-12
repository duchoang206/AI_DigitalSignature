import cv2
import numpy as np
from ultralytics import YOLO
from deepface import DeepFace
import os

class FaceEngine:
    def __init__(self, face_db_path):
        # Load YOLOv8 for detection (fast and accurate)
        self.detector = YOLO('yolov8n-face.pt') # Assuming the weights are available or will be downloaded
        self.face_db_path = face_db_path
        
        if not os.path.exists(self.face_db_path):
            os.makedirs(self.face_db_path)

    def identify_face(self, frame):
        """
        Identify a person from a frame.
        Returns: { 'name': '...', 'confidence': ... } or None
        """
        results = self.detector(frame, verbose=False)
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get face coordinates
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                face_img = frame[y1:y2, x1:x2]
                
                try:
                    # Recognize face using DeepFace against the DB
                    recognition = DeepFace.find(
                        img_path=face_img,
                        db_path=self.face_db_path,
                        enforce_detection=False,
                        model_name='Facenet512',
                        silent=True
                    )
                    
                    if len(recognition) > 0 and not recognition[0].empty:
                        # Extract name from filename (e.g. "Hoang_Xuan_Duc.jpg")
                        identity_path = recognition[0]['identity'][0]
                        name = os.path.basename(os.path.dirname(identity_path)) if os.path.isdir(identity_path) else os.path.basename(identity_path).split('.')[0]
                        distance = recognition[0]['distance'][0]
                        confidence = 1 - distance # Simplistic confidence mapping
                        
                        return {
                            'name': name.replace('_', ' '),
                            'confidence': float(confidence * 100),
                            'box': [x1, y1, x2, y2]
                        }
                except Exception as e:
                    print(f"Recognition error: {e}")
                    
        return None

    def enroll_employee(self, frame, name):
        """
        Save a face frame as the baseline for an employee.
        """
        results = self.detector(frame, verbose=False)
        if len(results) > 0 and len(results[0].boxes) > 0:
            box = results[0].boxes[0]
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            face_img = frame[y1:y2, x1:x2]
            
            # Save the face image
            save_path = os.path.join(self.face_db_path, f"{name.replace(' ', '_')}.jpg")
            cv2.imwrite(save_path, face_img)
            return True
        return False
