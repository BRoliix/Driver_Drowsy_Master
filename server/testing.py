import cv2
import dlib
import numpy as np
import pytest
from scipy.spatial import distance
import time
from tensorflow.keras.models import load_model
import pygame
from tensorflow.keras.optimizers.legacy import Adam

class DrowsinessTest:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.model = load_model("models/drowsiness_detector.keras", compile=False)
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
        pygame.mixer.init()
        self.alarm_sound = pygame.mixer.Sound("/Users/nekonyo/ai_project/Driver_Drowsy_Master/server/static/alarm.wav")
        
    def calculate_ear(self, eye_points):
        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        C = distance.euclidean(eye_points[0], eye_points[3])
        ear = (A + B) / (2.0 * C)
        return ear
    
    def run_live_test(self):
        cap = cv2.VideoCapture(0)
        EYE_AR_THRESH = 0.25
        EYE_AR_CONSEC_FRAMES = 20
        COUNTER = 0
        ALARM_ON = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            
            status = "Status: Active"
            status_color = (0, 255, 0)  # Green for active
            
            for face in faces:
                landmarks = self.predictor(gray, face)
                landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])
                
                left_eye = landmarks[36:42]
                right_eye = landmarks[42:48]
                
                left_ear = self.calculate_ear(left_eye)
                right_ear = self.calculate_ear(right_eye)
                ear = (left_ear + right_ear) / 2.0
                
                left_hull = cv2.convexHull(left_eye)
                right_hull = cv2.convexHull(right_eye)
                cv2.drawContours(frame, [left_hull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [right_hull], -1, (0, 255, 0), 1)
                
                if ear < EYE_AR_THRESH:
                    COUNTER += 1
                    if COUNTER >= EYE_AR_CONSEC_FRAMES:
                        if not ALARM_ON:
                            ALARM_ON = True
                            self.alarm_sound.play()
                        status = "Status: DROWSY!"
                        status_color = (0, 0, 255)  # Red for drowsy
                        cv2.putText(frame, "DROWSINESS ALERT!", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    COUNTER = 0
                    ALARM_ON = False
                
                cv2.putText(frame, f"EAR: {ear:.2f}", (300, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            cv2.putText(frame, status, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            
            cv2.imshow("Drowsiness Detection", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

# Unit Tests
def test_ear_calculation():
    detector = DrowsinessTest()
    eye_points = np.array([
        [0, 0], [1, 1], [2, 1],
        [3, 0], [2, -1], [1, -1]
    ])
    ear = detector.calculate_ear(eye_points)
    assert ear > 0
    assert isinstance(ear, float)

def test_detector_initialization():
    detector = DrowsinessTest()
    assert detector.detector is not None
    assert detector.predictor is not None
    assert detector.model is not None

if __name__ == "__main__":
    print("Running unit tests...")
    pytest.main([__file__])
    
    print("\nStarting live drowsiness detection...")
    detector = DrowsinessTest()
    detector.run_live_test()
