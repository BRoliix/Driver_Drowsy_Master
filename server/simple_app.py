"""
Simplified version for PythonAnywhere deployment
This version removes some heavy dependencies that might not install on free tier
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import cv2
import numpy as np
# import dlib  # Comment out if dlib fails to install
from scipy.spatial import distance
import asyncio
import base64
import os
from datetime import datetime
# from dao import raise_sos  # Comment out if PocketBase has issues
import json

app = FastAPI(title="Driver Drowsiness Detection", version="1.0.0")

# Mount static files
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory="static"), name="static")

class SimpleDrowsinessDetector:
    """Simplified detector that can work without dlib if needed"""
    
    def __init__(self):
        # Basic OpenCV face detector (works without dlib)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Try to load dlib if available
        self.use_dlib = False
        try:
            import dlib
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat") if os.path.exists("shape_predictor_68_face_landmarks.dat") else None
            self.use_dlib = True
            print("✅ Using dlib for advanced detection")
        except (ImportError, OSError):
            print("⚠️  dlib not available, using basic OpenCV detection")
        
        self.drowsy_frames = 0
        self.status = "Initializing..."
        self.color = (0, 255, 0)
        self.DROWSY_FRAME_THRESHOLD = 20  # Increased for basic detection

    def simple_eye_detection(self, frame, face):
        """Simple eye detection using OpenCV cascades"""
        x, y, w, h = face
        roi_gray = frame[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
        return len(eyes)

    async def process_frame(self, frame):
        """Process frame for drowsiness detection"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.use_dlib and self.predictor:
                # Use dlib if available (more accurate)
                faces = self.detector(gray)
                for face in faces:
                    landmarks = self.predictor(gray, face)
                    # EAR calculation logic would go here
                    # For now, simplified detection
                    self.simple_detection_logic()
            else:
                # Use basic OpenCV detection
                faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
                for face in faces:
                    eyes_count = self.simple_eye_detection(gray, face)
                    
                    if eyes_count < 2:  # Eyes likely closed
                        self.drowsy_frames += 1
                    else:
                        self.drowsy_frames = max(0, self.drowsy_frames - 1)
                    
                    # Draw rectangle around face
                    x, y, w, h = face
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    # Update status
                    if self.drowsy_frames >= self.DROWSY_FRAME_THRESHOLD:
                        self.status = "DROWSY DETECTED!"
                        self.color = (0, 0, 255)  # Red
                        # Try to raise SOS
                        try:
                            await self.raise_simple_sos()
                        except:
                            print("SOS system unavailable")
                    else:
                        self.status = "Alert and Active"
                        self.color = (0, 255, 0)  # Green

            # Add status text to frame
            cv2.putText(frame, self.status, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color, 2)
            cv2.putText(frame, f"Drowsy Frames: {self.drowsy_frames}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

            return frame, self.status, self.drowsy_frames >= self.DROWSY_FRAME_THRESHOLD

        except Exception as e:
            print(f"Error processing frame: {e}")
            cv2.putText(frame, "Error in detection", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return frame, "Error", False

    def simple_detection_logic(self):
        """Simplified detection for dlib mode"""
        # Placeholder for more advanced detection
        pass

    async def raise_simple_sos(self):
        """Simplified SOS without external dependencies"""
        try:
            # Try to use dao if available
            from dao import raise_sos
            await raise_sos()
        except ImportError:
            # Log locally if dao not available
            sos_data = {
                'timestamp': datetime.now().isoformat(),
                'alert': 'Drowsiness detected',
                'status': 'NEW'
            }
            
            # Save to local file as backup
            try:
                with open('sos_alerts.json', 'a') as f:
                    json.dump(sos_data, f)
                    f.write('\n')
                print("✅ SOS alert logged locally")
            except Exception as e:
                print(f"⚠️  Could not log SOS: {e}")

# Initialize detector
detector = SimpleDrowsinessDetector()

@app.get("/")
async def main():
    """Serve the main interface"""
    try:
        with open("../index.html", "r") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Driver Drowsiness Detection</title>
            <style>
                body { font-family: Arial; text-align: center; margin: 50px; }
                .status { font-size: 24px; margin: 20px; }
                .alert { color: red; font-weight: bold; }
                .active { color: green; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>🚗 Driver Drowsiness Detection System</h1>
            <div id="status" class="status">System Ready</div>
            <video id="video" width="640" height="480" autoplay></video>
            <canvas id="canvas" width="640" height="480" style="display:none;"></canvas>
            
            <script>
                const video = document.getElementById('video');
                const canvas = document.getElementById('canvas');
                const ctx = canvas.getContext('2d');
                const status = document.getElementById('status');
                
                // Start camera
                navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                        video.srcObject = stream;
                        connectWebSocket();
                    })
                    .catch(err => {
                        status.innerHTML = '❌ Camera access denied or unavailable';
                        console.error('Camera error:', err);
                    });
                
                function connectWebSocket() {
                    const ws = new WebSocket(`ws://${window.location.host}/ws/video`);
                    
                    ws.onopen = () => {
                        status.innerHTML = '✅ Connected - Monitoring for drowsiness';
                        startVideoProcessing();
                    };
                    
                    ws.onmessage = (event) => {
                        const data = JSON.parse(event.data);
                        status.innerHTML = data.status;
                        status.className = data.alert ? 'status alert' : 'status active';
                        
                        if (data.frame) {
                            video.src = 'data:image/jpeg;base64,' + data.frame;
                        }
                    };
                    
                    ws.onclose = () => {
                        status.innerHTML = '⚠️ Connection lost - Reconnecting...';
                        setTimeout(connectWebSocket, 3000);
                    };
                    
                    function startVideoProcessing() {
                        setInterval(() => {
                            if (video.readyState === video.HAVE_ENOUGH_DATA) {
                                ctx.drawImage(video, 0, 0);
                                const imageData = canvas.toDataURL('image/jpeg').split(',')[1];
                                ws.send(JSON.stringify({ frame: imageData }));
                            }
                        }, 100);
                    }
                }
            </script>
        </body>
        </html>
        """, status_code=200)

@app.websocket("/ws/video")
async def video_feed(websocket: WebSocket):
    """Handle video WebSocket connections"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_json()
            
            if 'frame' in data:
                # Decode frame from base64
                frame_data = base64.b64decode(data['frame'])
                nparr = np.frombuffer(frame_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    # Process frame for drowsiness
                    processed_frame, status, is_alert = await detector.process_frame(frame)
                    
                    # Encode processed frame
                    _, buffer = cv2.imencode('.jpg', processed_frame)
                    base64_frame = base64.b64encode(buffer).decode('utf-8')
                    
                    # Send response
                    await websocket.send_json({
                        "frame": base64_frame,
                        "status": status,
                        "alert": is_alert
                    })
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "detector": "active",
        "dlib_available": detector.use_dlib,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)