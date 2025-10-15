from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
from scipy.spatial import distance
import asyncio
import base64
import json
import os
from datetime import datetime
from dao import raise_sos

# Try to import dlib, fallback to OpenCV if not available (for Railway deployment)
try:
    import dlib
    DLIB_AVAILABLE = True
    print("✅ dlib loaded successfully")
except ImportError:
    DLIB_AVAILABLE = False
    print("⚠️  dlib not available, using OpenCV fallback")

app = FastAPI()
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory="static"), name="static")

class DrowsinessDetector:
    def __init__(self):
        # Initialize based on available libraries
        if DLIB_AVAILABLE:
            self.detector = dlib.get_frontal_face_detector()
            predictor_path = "shape_predictor_68_face_landmarks.dat"
            if os.path.exists(predictor_path):
                self.predictor = dlib.shape_predictor(predictor_path)
                self.use_advanced = True
                print("✅ Using dlib with facial landmarks")
            else:
                self.use_advanced = False
                print("⚠️  Landmark file not found, using basic dlib")
        else:
            # Fallback to OpenCV
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            self.use_advanced = False
            print("✅ Using OpenCV cascades")
        
        # TensorFlow model temporarily disabled due to Python 3.14 compatibility
        # self.model = tf.keras.models.load_model("models/drowsiness_detector.keras", compile=False)
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

    def simple_eye_detection(self, gray, face_rect):
        """Simple eye detection using OpenCV cascades"""
        x, y, w, h = face_rect
        roi_gray = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
        return len(eyes)

    async def process_frame(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            play_alarm = False
            current_time = datetime.now()
            can_alert = (self.last_alert_time is None or 
                       (current_time - self.last_alert_time).total_seconds() > self.ALERT_COOLDOWN)

            if DLIB_AVAILABLE and hasattr(self, 'detector'):
                # Use dlib detection
                faces = self.detector(gray)
                
                if len(faces) == 0:
                    self.drowsy_frames = 0
                    self.status = "No face detected"
                    return frame, self.status, play_alarm

                for face in faces:
                    # Draw face rectangle
                    x, y, w, h = face.left(), face.top(), face.width(), face.height()
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    
                    if self.use_advanced and hasattr(self, 'predictor'):
                        # Advanced landmark detection
                        landmarks = self.predictor(gray, face)
                        landmarks = np.array([[p.x, p.y] for p in landmarks.parts()])
                        
                        # Extract eye regions
                        left_eye = landmarks[36:42]
                        right_eye = landmarks[42:48]
                        
                        left_ear = self.calculate_ear(left_eye)
                        right_ear = self.calculate_ear(right_eye)
                        ear = (left_ear + right_ear) / 2.0
                        
                        # Draw eye contours
                        left_hull = cv2.convexHull(left_eye)
                        right_hull = cv2.convexHull(right_eye)
                        cv2.drawContours(frame, [left_hull], -1, (0, 255, 0), 1)
                        cv2.drawContours(frame, [right_hull], -1, (0, 255, 0), 1)
                        
                        # Display EAR value
                        cv2.putText(frame, f"EAR: {ear:.2f}", (300, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                        
                        if ear < 0.25:  # Eyes closed threshold
                            self.drowsy_frames += 1
                        else:
                            self.drowsy_frames = 0
                    else:
                        # Basic dlib detection without landmarks - simple drowsiness check
                        eyes_count = self.simple_eye_detection(gray, (x, y, w, h))
                        if eyes_count < 2:
                            self.drowsy_frames += 1
                        else:
                            self.drowsy_frames = max(0, self.drowsy_frames - 1)
            else:
                # Use OpenCV cascade detection
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                
                if len(faces) == 0:
                    self.drowsy_frames = 0
                    self.status = "No face detected"
                    return frame, self.status, play_alarm

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    # Simple eye detection for OpenCV path
                    eyes_count = self.simple_eye_detection(gray, (x, y, w, h))
                    
                    if eyes_count < 2:  # Likely eyes closed
                        self.drowsy_frames += 1
                    else:
                        self.drowsy_frames = max(0, self.drowsy_frames - 1)

            # Check for drowsiness
            if self.drowsy_frames >= self.DROWSY_FRAME_THRESHOLD:
                self.status = "DROWSY!"
                if self.status != self.previous_status or can_alert:
                    play_alarm = True
                    print(f"🚨 DROWSY DETECTED! Calling raise_sos() - Frames: {self.drowsy_frames}")
                    try:
                        raise_sos()
                    except Exception as e:
                        print(f"❌ Error in raise_sos: {e}")
                    self.last_alert_time = current_time
                self.color = (0, 0, 255)
            else:
                self.status = "Active"
                self.color = (0, 255, 0)

            # Display status
            cv2.putText(frame, self.status, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color, 2)
            cv2.putText(frame, f"Drowsy Frames: {self.drowsy_frames}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            self.previous_status = self.status
            return frame, self.status, play_alarm

        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, "Error processing", False

detector = DrowsinessDetector()

@app.websocket("/ws/video")
async def video_feed(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive frame from client (browser camera)
            message = await websocket.receive_text()
            data = json.loads(message)  # Parse incoming frame data
            
            # Decode base64 image
            frame_data = base64.b64decode(data['frame'])
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
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
        pass

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
            <video id="webcam" autoplay muted style="display: none; width: 100%; max-width: 640px;"></video>
            <canvas id="canvas" style="display: none;"></canvas>
            <img id="video" alt="Video feed" style="display: none;">
            <div id="status">Click 'Start Detection' to begin</div>
        </div>
        <script>
            let ws = null;
            const video = document.getElementById('video');
            const webcam = document.getElementById('webcam');
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            const status = document.getElementById('status');
            const startButton = document.getElementById('startButton');
            let isDetectionRunning = false;
            let audioContext = null;
            let alarmBuffer = null;
            let currentAlarm = null;
            let stream = null;

            function createBeepSound(frequency = 800, duration = 500) {
                if (!audioContext) return null;
                
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = frequency;
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
                
                return { oscillator, gainNode, duration };
            }

            function playAlarm() {
                if (!currentAlarm && audioContext) {
                    console.log("🚨 Playing alarm sound");
                    const beep = createBeepSound(800, 500);
                    if (beep) {
                        currentAlarm = beep.oscillator;
                        beep.oscillator.start();
                        beep.oscillator.stop(audioContext.currentTime + beep.duration / 1000);
                        beep.oscillator.onended = () => {
                            currentAlarm = null;
                        };
                    }
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
                
                try {
                    // Request camera access
                    stream = await navigator.mediaDevices.getUserMedia({ video: true });
                    webcam.srcObject = stream;
                    webcam.style.display = 'block';
                    video.style.display = 'block';
                    
                    // Set canvas size
                    webcam.onloadedmetadata = function() {
                        canvas.width = webcam.videoWidth;
                        canvas.height = webcam.videoHeight;
                    };
                    
                    if (!audioContext) {
                        audioContext = new (window.AudioContext || window.webkitAudioContext)();
                        console.log("🔊 Audio context initialized");
                    }
                    
                    isDetectionRunning = true;
                    startButton.textContent = 'Detection Running';
                    
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    ws = new WebSocket(`${protocol}//${window.location.host}/ws/video`);
                    
                    ws.onopen = function() {
                        // Start sending frames
                        sendFrames();
                    };
                    
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
                        if (stream) {
                            stream.getTracks().forEach(track => track.stop());
                        }
                    };
                    
                    ws.onerror = function(err) {
                        console.error('WebSocket error:', err);
                        ws.close();
                    };
                } catch (err) {
                    console.error('Error accessing camera:', err);
                    status.textContent = 'Error accessing camera. Please allow camera permissions.';
                }
            }
            
            function sendFrames() {
                if (!isDetectionRunning || !ws || ws.readyState !== WebSocket.OPEN) return;
                
                ctx.drawImage(webcam, 0, 0, canvas.width, canvas.height);
                canvas.toBlob(function(blob) {
                    const reader = new FileReader();
                    reader.onload = function() {
                        const base64 = reader.result.split(',')[1];
                        ws.send(JSON.stringify({ frame: base64 }));
                    };
                    reader.readAsDataURL(blob);
                }, 'image/jpeg', 0.8);
                
                setTimeout(sendFrames, 100); // Send frame every 100ms
            }

            startButton.addEventListener('click', startDetection);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
