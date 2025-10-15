from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import dlib
from scipy.spatial import distance
import asyncio
import base64
import os
from datetime import datetime
from dao import raise_sos

app = FastAPI()
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory="static"), name="static")

class DrowsinessDetector:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        # TensorFlow model temporarily disabled due to Python 3.14 compatibility
        # self.model = tf.keras.models.load_model("models/drowsiness_detector.keras", compile=False)
        # self.model.compile(
        #     optimizer=tf.keras.optimizers.legacy.Adam(learning_rate=0.001),
        #     loss='binary_crossentropy',
        #     metrics=['accuracy']
        # )
        self.model = None  # Placeholder
        self.drowsy_frames = 0
        self.status = ""
        self.color = (0, 0, 0)
        self.last_alert_time = None
        self.ALERT_COOLDOWN = 30
        self.DROWSY_FRAME_THRESHOLD = 8
        self.previous_status = ""

    def calculate_ear(self, eye_points):
        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        C = distance.euclidean(eye_points[0], eye_points[3])
        ear = (A + B) / (2.0 * C)
        return ear

    async def process_frame(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            play_alarm = False

            if len(faces) == 0:
                self.drowsy_frames = 0
                self.status = "No face detected"
                return frame, self.status, play_alarm

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

                current_time = datetime.now()
                can_alert = (self.last_alert_time is None or 
                           (current_time - self.last_alert_time).total_seconds() > self.ALERT_COOLDOWN)

                if ear < 0.25:
                    self.drowsy_frames += 1
                    if self.drowsy_frames >= self.DROWSY_FRAME_THRESHOLD:
                        self.status = "DROWSY!"
                        if self.status != self.previous_status or can_alert:
                            play_alarm = True
                            raise_sos()
                            self.last_alert_time = current_time
                        self.color = (0, 0, 255)
                else:
                    self.drowsy_frames = 0
                    self.status = "Active"
                    self.color = (0, 255, 0)

                cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                cv2.putText(frame, self.status, (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color, 2)

                self.previous_status = self.status

            return frame, self.status, play_alarm

        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, "Error processing", False

detector = DrowsinessDetector()

@app.websocket("/ws/video")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            processed_frame, status, play_alarm = await detector.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', processed_frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            await websocket.send_json({
                "frame": base64_frame,
                "status": status,
                "play_alarm": play_alarm
            })
            await asyncio.sleep(0.03)
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        cap.release()

@app.get("/")
async def get_html():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Drowsiness Detection System</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            #video {
                width: 100%;
                max-width: 640px;
                border-radius: 5px;
                margin: 20px 0;
            }
            #status {
                padding: 10px;
                margin: 10px 0;
                font-weight: bold;
                border-radius: 5px;
            }
            #startButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px 0;
            }
            #startButton:hover {
                background-color: #45a049;
            }
            .active {
                background-color: #d4edda;
                color: #155724;
            }
            .drowsy {
                background-color: #f8d7da;
                color: #721c24;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Drowsiness Detection System</h1>
            <button id="startButton">Start Detection</button>
            <img id="video" alt="Video feed" style="display: none;">
            <div id="status">Click 'Start Detection' to begin</div>
        </div>
        <script>
            let ws = null;
            const video = document.getElementById('video');
            const status = document.getElementById('status');
            const startButton = document.getElementById('startButton');
            let isDetectionRunning = false;
            let audioContext = null;
            let alarmBuffer = null;
            let currentAlarm = null;

            async function loadAlarmSound() {
                const response = await fetch('/static/alarm.wav');
                const arrayBuffer = await response.arrayBuffer();
                alarmBuffer = await audioContext.decodeAudioData(arrayBuffer);
            }

            function playAlarm() {
                if (alarmBuffer && !currentAlarm) {
                    const source = audioContext.createBufferSource();
                    source.buffer = alarmBuffer;
                    source.connect(audioContext.destination);
                    source.start(0);
                    source.onended = () => {
                        currentAlarm = null;
                    };
                    currentAlarm = source;
                }
            }

            function stopAlarm() {
                if (currentAlarm) {
                    currentAlarm.stop();
                    currentAlarm = null;
                }
            }

            async function startDetection() {
                if (isDetectionRunning) return;
                if (!audioContext) {
                    audioContext = new (window.AudioContext || window.webkitAudioContext)();
                    await loadAlarmSound();
                }
                video.style.display = 'block';
                isDetectionRunning = true;
                startButton.textContent = 'Detection Running';
                ws = new WebSocket(`ws://${window.location.host}/ws/video`);
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    video.src = `data:image/jpeg;base64,${data.frame}`;
                    status.textContent = data.status;
                    status.className = '';
                    if (data.status.includes('Active')) {
                        status.classList.add('active');
                        stopAlarm();
                    } else if (data.status.includes('DROWSY')) {
                        status.classList.add('drowsy');
                        if (data.play_alarm) {
                            playAlarm();
                        }
                    }
                };
                ws.onclose = function() {
                    status.textContent = 'Connection closed';
                    isDetectionRunning = false;
                    startButton.textContent = 'Start Detection';
                    stopAlarm();
                    setTimeout(startDetection, 1000);
                };
                ws.onerror = function(err) {
                    console.error('WebSocket error:', err);
                    ws.close();
                };
            }

            startButton.addEventListener('click', startDetection);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
