import face_recognition
import numpy as np
import cv2
from typing import List, Dict, Optional, Tuple
import pickle
import os
from pathlib import Path
from app.core.config import settings


class FaceRecognitionService:
    """Service for face recognition operations"""
    
    def __init__(self):
        self.tolerance = settings.FACE_RECOGNITION_TOLERANCE
        self.model = settings.FACE_DETECTION_MODEL
        self.encodings_dir = Path(settings.FACE_ENCODINGS_DIR)
        self.encodings_dir.mkdir(parents=True, exist_ok=True)
    
    def detect_faces(self, image_path: str) -> List[Dict]:
        """
        Detect all faces in an image
        Returns: List of face locations and landmarks
        """
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image, model=self.model)
        face_landmarks = face_recognition.face_landmarks(image)
        
        results = []
        for i, (location, landmarks) in enumerate(zip(face_locations, face_landmarks)):
            top, right, bottom, left = location
            results.append({
                "face_index": i,
                "location": {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
                },
                "landmarks": landmarks
            })
        
        return results
    
    def extract_encoding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Extract face encoding from image
        Returns: 128-dimensional face encoding or None if no face found
        """
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image, model=self.model)
        
        if len(encodings) == 0:
            return None
        
        # Return first face encoding
        return encodings[0]
    
    def extract_multiple_encodings(self, image_path: str) -> List[np.ndarray]:
        """
        Extract all face encodings from image
        Returns: List of face encodings
        """
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image, model=self.model)
        return encodings
    
    def compare_faces(
        self, 
        known_encoding: np.ndarray, 
        unknown_encoding: np.ndarray,
        tolerance: Optional[float] = None
    ) -> Tuple[bool, float]:
        """
        Compare two face encodings
        Returns: (is_match, distance)
        """
        if tolerance is None:
            tolerance = self.tolerance
        
        distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
        is_match = distance <= tolerance
        
        return is_match, float(distance)
    
    def recognize_face(
        self,
        image_path: str,
        known_encodings: List[np.ndarray],
        known_names: List[str],
        tolerance: Optional[float] = None
    ) -> List[Dict]:
        """
        Recognize faces in image against known encodings
        Returns: List of recognition results
        """
        if tolerance is None:
            tolerance = self.tolerance
        
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image, model=self.model)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        results = []
        for encoding, location in zip(face_encodings, face_locations):
            # Compare with all known faces
            matches = face_recognition.compare_faces(
                known_encodings, 
                encoding, 
                tolerance=tolerance
            )
            distances = face_recognition.face_distance(known_encodings, encoding)
            
            # Find best match
            if True in matches:
                best_match_index = np.argmin(distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]
                    confidence = 1 - distances[best_match_index]
                else:
                    name = "Unknown"
                    confidence = 0.0
            else:
                name = "Unknown"
                confidence = 0.0
            
            top, right, bottom, left = location
            results.append({
                "name": name,
                "confidence": float(confidence),
                "distance": float(distances[best_match_index]) if True in matches else None,
                "location": {
                    "top": top,
                    "right": right,
                    "bottom": bottom,
                    "left": left
                }
            })
        
        return results
    
    def save_encoding(self, encoding: np.ndarray, user_id: str, name: str) -> str:
        """
        Save face encoding to disk
        Returns: path to saved file
        """
        filename = f"{user_id}_{name}.pkl"
        filepath = self.encodings_dir / filename
        
        with open(filepath, 'wb') as f:
            pickle.dump(encoding, f)
        
        return str(filepath)
    
    def load_encoding(self, filepath: str) -> np.ndarray:
        """Load face encoding from disk"""
        with open(filepath, 'rb') as f:
            encoding = pickle.load(f)
        return encoding
    
    def check_liveness(self, image_path: str) -> Dict:
        """
        Simple liveness detection (anti-spoofing)
        Checks for basic signs of real face vs photo
        """
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Check image quality metrics
        # 1. Laplacian variance (blur detection)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_blurry = laplacian_var < 100
        
        # 2. Color analysis (photos tend to have less color variation)
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color_var = np.var(hsv)
        is_photo = color_var < 1000
        
        # Simple scoring
        liveness_score = 0.5
        if not is_blurry:
            liveness_score += 0.25
        if not is_photo:
            liveness_score += 0.25
        
        return {
            "is_live": liveness_score > 0.6,
            "liveness_score": float(liveness_score),
            "is_blurry": is_blurry,
            "blur_score": float(laplacian_var),
            "color_variance": float(color_var)
        }
    
    def draw_faces(self, image_path: str, output_path: str, faces: List[Dict]) -> str:
        """
        Draw rectangles and labels on detected faces
        Returns: path to output image
        """
        image = cv2.imread(image_path)
        
        for face in faces:
            loc = face["location"]
            name = face.get("name", "Unknown")
            confidence = face.get("confidence", 0)
            
            # Draw rectangle
            cv2.rectangle(
                image,
                (loc["left"], loc["top"]),
                (loc["right"], loc["bottom"]),
                (0, 255, 0),
                2
            )
            
            # Draw label
            label = f"{name} ({confidence:.2f})"
            cv2.putText(
                image,
                label,
                (loc["left"], loc["top"] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        cv2.imwrite(output_path, image)
        return output_path


# Create singleton instance
face_service = FaceRecognitionService()
