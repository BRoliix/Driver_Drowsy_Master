import cv2
import numpy as np
import dlib
from imutils import face_utils
import pyglet
from datetime import datetime
import dao
import platform
import streamlit as st
import threading
import time

def sound_alarm():
    try:
        music = pyglet.resource.media('alarm.wav')
        music.play()
    except Exception as e:
        st.error(f"Error playing alarm: {e}")

def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    if ratio > 0.25:
        return 2
    elif 0.21 < ratio <= 0.25:
        return 1
    else:
        return 0

def get_video_capture():
    """Determine appropriate video backend based on the OS."""
    system = platform.system()
    if system == "Windows":
        return cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow on Windows
    else:
        return cv2.VideoCapture(0)  # Default backend for Linux and macOS

class DrowsinessDetector:
    def __init__(self):
        self.cap = get_video_capture()
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.frame = None
        self.running = True

    def process_frame(self):
        sleep = 0
        drowsy = 0
        active = 0
        status = ""
        color = (0, 0, 0)
        last_alert_time = None
        ALERT_COOLDOWN = 30
        previous_status = ""

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue

            self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)

            for face in faces:
                landmarks = self.predictor(gray, face)
                landmarks = face_utils.shape_to_np(landmarks)

                left_blink = blinked(landmarks[36], landmarks[37],
                                     landmarks[38], landmarks[41], landmarks[40], landmarks[39])
                right_blink = blinked(landmarks[42], landmarks[43],
                                      landmarks[44], landmarks[47], landmarks[46], landmarks[45])

                current_time = datetime.now()
                can_alert = (last_alert_time is None or
                             (current_time - last_alert_time).total_seconds() > ALERT_COOLDOWN)

                if left_blink == 0 or right_blink == 0:
                    sleep += 1
                    drowsy = 0
                    active = 0
                    if sleep > 6:
                        status = "SLEEPING !!!"
                        if status != previous_status or can_alert:
                            try:
                                sound_alarm()
                                dao.raise_sos()
                                last_alert_time = current_time
                            except Exception as e:
                                print(f"Error raising alert: {e}")
                        color = (255, 0, 0)

                elif left_blink == 1 or right_blink == 1:
                    sleep = 0
                    active = 0
                    drowsy += 1
                    if drowsy > 6:
                        status = "Drowsy !"
                        if status != previous_status or can_alert:
                            try:
                                sound_alarm()
                                dao.raise_sos()
                                last_alert_time = current_time
                            except Exception as e:
                                print(f"Error raising alert: {e}")
                        color = (0, 0, 255)

                else:
                    drowsy = 0
                    sleep = 0
                    active += 1
                    if active > 6:
                        status = "Active :)"
                        color = (0, 255, 0)

                previous_status = status
                cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

            time.sleep(0.01)  # Small delay to make the thread responsive

        self.cap.release()

def main():
    st.title("Real-Time Drowsiness Detection")
    st.write("Click the button below to start the detection system.")

    detector = DrowsinessDetector()
    placeholder = st.empty()

    def run_detection():
        detector.process_frame()

    thread = threading.Thread(target=run_detection)
    if st.button("Start Detection"):
        thread.start()

    while detector.running:
        if detector.frame is not None:
            placeholder.image(detector.frame, channels="RGB")
        time.sleep(0.03)  # Control frame update rate

    detector.running = False
    thread.join()

if __name__ == "__main__":
    main()
