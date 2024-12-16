
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
        self.sleep = 0
        self.drowsy = 0
        self.active = 0
        self.status = ""
        self.color = (0, 0, 0)
        self.last_alert_time = None
        self.ALERT_COOLDOWN = 30
        self.previous_status = ""

    def compute(self, ptA, ptB):
        return np.linalg.norm(ptA - ptB)

    def blinked(self, a, b, c, d, e, f):
        up = self.compute(b, d) + self.compute(c, e)
        down = self.compute(a, f)
        ratio = up / (2.0 * down)
        
        if ratio > 0.25:
            return 2
        elif ratio > 0.21 and ratio <= 0.25:
            return 1
        else:
            return 0

    async def process_frame(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            play_alarm = False

            if len(faces) == 0:
                self.sleep = 0
                self.drowsy = 0
                self.active = 0
                self.status = "No face detected"
                return frame, self.status, play_alarm

            for face in faces:
                landmarks = self.predictor(gray, face)
                landmarks = face_utils.shape_to_np(landmarks)

                # Draw facial landmarks
                for n in range(0, 68):
                    (x, y) = landmarks[n]
                    cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)

                left_blink = self.blinked(landmarks[36], landmarks[37],
                                        landmarks[38], landmarks[41], landmarks[40], landmarks[39])
                right_blink = self.blinked(landmarks[42], landmarks[43],
                                         landmarks[44], landmarks[47], landmarks[46], landmarks[45])

                current_time = datetime.now()
                can_alert = (self.last_alert_time is None or 
                            (current_time - self.last_alert_time).total_seconds() > self.ALERT_COOLDOWN)

                if left_blink == 0 or right_blink == 0:
                    self.sleep += 1
                    self.drowsy = 0
                    self.active = 0
                    if self.sleep > 30:
                        self.status = "SLEEPING !!!"
                        if self.status != self.previous_status or can_alert:
                            play_alarm = True
                            raise_sos()
                            self.last_alert_time = current_time
                        self.color = (255, 0, 0)

                elif left_blink == 1 or right_blink == 1:
                    self.sleep = 0
                    self.active = 0
                    self.drowsy += 1
                    if self.drowsy > 30:
                        self.status = "Drowsy !"
                        if self.status != self.previous_status or can_alert:
                            play_alarm = True
                            raise_sos()
                            self.last_alert_time = current_time
                        self.color = (0, 0, 255)

                else:
                    self.drowsy = 0
                    self.sleep = 0
                    self.active += 1
                    if self.active > 6:
                        self.status = "Active :)"
                        self.color = (0, 255, 0)

                self.previous_status = self.status
                cv2.putText(frame, self.status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.color, 3)

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
        <title>Sleeping Detection</title>
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
                    } else if (data.status.includes('SLEEPING')) {
                        status.classList.add('sleeping');
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
