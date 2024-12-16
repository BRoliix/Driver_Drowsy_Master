# main.py
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
import dlib
from imutils import face_utils
import asyncio
import base64
import os
from datetime import datetime, timedelta

app = FastAPI()

# Create static directory if it doesn't exist
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

class DrowsinessDetector:
    def __init__(self):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
        self.cap = None
        self.sleep_start_time = None
        self.last_alert_time = None
        self.ALERT_COOLDOWN = 30
        
    def compute(self, ptA, ptB):
        return np.linalg.norm(ptA - ptB)
    
    def blinked(self, a, b, c, d, e, f):
        up = self.compute(b, d) + self.compute(c, e)
        down = self.compute(a, f)
        ratio = up / (2.0 * down)
        return 2 if ratio > 0.25 else 1 if 0.21 < ratio <= 0.25 else 0

    async def process_frame(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            status = "No face detected"
            color = (0, 0, 0)
            play_alarm = False
            send_sos = False
            
            if len(faces) > 0:  # If face is detected
                face = faces[0]  # Take the first face
                landmarks = self.predictor(gray, face)
                landmarks = face_utils.shape_to_np(landmarks)

                left_blink = self.blinked(landmarks[36], landmarks[37],
                                        landmarks[38], landmarks[41], landmarks[40], landmarks[39])
                right_blink = self.blinked(landmarks[42], landmarks[43],
                                        landmarks[44], landmarks[47], landmarks[46], landmarks[45])

                current_time = datetime.now()
                can_alert = (self.last_alert_time is None or
                            (current_time - self.last_alert_time).total_seconds() > self.ALERT_COOLDOWN)

                if left_blink == 0 or right_blink == 0:
                    if self.sleep_start_time is None:
                        self.sleep_start_time = datetime.now()
                    elif datetime.now() - self.sleep_start_time >= timedelta(seconds=6):
                        status = "SLEEPING !!!"
                        color = (255, 0, 0)
                        if can_alert:
                            play_alarm = True
                            send_sos = True
                            self.last_alert_time = current_time
                    else:
                        status = "Eyes Closed"
                        color = (0, 255, 255)
                elif left_blink == 1 or right_blink == 1:
                    self.sleep_start_time = None
                    status = "Drowsy !"
                    color = (0, 0, 255)
                else:
                    self.sleep_start_time = None
                    status = "Active :)"
                    color = (0, 255, 0)
            else:
                # Don't reset sleep_start_time when face is not detected
                if self.sleep_start_time is not None:
                    current_time = datetime.now()
                    if datetime.now() - self.sleep_start_time >= timedelta(seconds=6):
                        status = "SLEEPING !!!"
                        color = (255, 0, 0)
                        if self.last_alert_time is None or (current_time - self.last_alert_time).total_seconds() > self.ALERT_COOLDOWN:
                            play_alarm = True
                            send_sos = True
                            self.last_alert_time = current_time

            cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)
            
            return frame, status, play_alarm, send_sos
        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, "Error processing", False, False
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
                
            processed_frame, status, play_alarm, send_sos = await detector.process_frame(frame)
            _, buffer = cv2.imencode('.jpg', processed_frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            
            await websocket.send_json({
                "frame": base64_frame,
                "status": status,
                "play_alarm": play_alarm,
                "send_sos": send_sos
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
        <title>Drowsiness Detection</title>
        <style>
            body {
                font-family: Arial;
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
            .active { background-color: #d4edda; color: #155724; }
            .drowsy { background-color: #fff3cd; color: #856404; }
            .sleeping { background-color: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Drowsiness Detection System</h1>
            <button id="startButton">Start Detection</button>
            <img id="video" alt="Video feed" style="display: none;">
            <div id="status">Click 'Start Detection' to begin</div>
        </div>
        
        <audio id="alarm" src="/static/alarm.wav" preload="auto"></audio>
        
        <script>
            let ws = null;
            const video = document.getElementById('video');
            const status = document.getElementById('status');
            const alarm = document.getElementById('alarm');
            const startButton = document.getElementById('startButton');
            let isDetectionRunning = false;

            // Initialize audio context after user interaction
            function initializeAudio() {
                alarm.play().then(() => {
                    alarm.pause();
                    alarm.currentTime = 0;
                }).catch(e => console.log('Error initializing audio:', e));
            }

            function startDetection() {
                if (isDetectionRunning) return;
                
                initializeAudio();
                video.style.display = 'block';
                isDetectionRunning = true;
                startButton.textContent = 'Detection Running';
                
                ws = new WebSocket(`ws://${window.location.host}/ws/video`);
                
                ws.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    video.src = `data:image/jpeg;base64,${data.frame}`;
                    status.textContent = data.status;
                    
                    // Update status styling
                    status.className = '';
                    if (data.status.includes('Active')) {
                        status.classList.add('active');
                    } else if (data.status.includes('Drowsy')) {
                        status.classList.add('drowsy');
                    } else if (data.status.includes('SLEEPING')) {
                        status.classList.add('sleeping');
                    }
                    
                    if (data.play_alarm) {
                        alarm.play().catch(e => console.log('Error playing alarm:', e));
                    } else {
                        alarm.pause();
                        alarm.currentTime = 0;
                    }
                    
                    if (data.send_sos) {
                        console.log('SOS signal sent!');
                    }
                };
                
                ws.onclose = function() {
                    status.textContent = 'Connection closed';
                    isDetectionRunning = false;
                    startButton.textContent = 'Start Detection';
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
