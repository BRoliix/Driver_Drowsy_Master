The code utilizes the shape_predictor_68_face_landmarks.dat model to detect the eyes' position and determine if they are open or closed. If the eyes remain closed for over 10 seconds, an alarm is triggered to alert the user. Additionally, the system sends an SOS signal to the database, which can be viewed by the administrator through a website interface.

To achieve this functionality, the code employs computer vision techniques to identify facial landmarks, particularly focusing on the eyes. By analyzing the spatial arrangement of these landmarks, the code can ascertain whether the eyes are open or closed.

If the eyes are detected as closed for a continuous duration exceeding 10 seconds, the system activates an alarm to notify the user, thereby preventing potential hazards due to prolonged eye closure, such as drowsiness or fatigue.

Furthermore, to ensure safety and facilitate monitoring, the system sends an SOS signal to a centralized database. This signal contains relevant information indicating the occurrence of prolonged eye closure. The database stores these SOS signals, allowing the administrator to access and review them through a dedicated website interface.

By integrating these functionalities, the system enhances user safety by providing timely alerts for extended periods of eye closure and enables efficient monitoring and management of critical events through the centralized database and web-based administration interface.


# Drowsiness Detection System Documentation

## Overview
This application is a real-time drowsiness detection system built with FastAPI and OpenCV. It monitors a user's face through their webcam and detects signs of drowsiness or sleeping based on eye movements.

## Technical Stack
- **Backend**: FastAPI
- **Computer Vision**: OpenCV, dlib
- **Frontend**: HTML, JavaScript
- **WebSocket**: For real-time video streaming
- **Audio**: Web Audio API for alerts

## Installation Requirements

**Required Dependencies:**
- FastAPI
- OpenCV (cv2)
- dlib
- imutils
- numpy
- asyncio

**Required Files:**
- shape_predictor_68_face_landmarks.dat (facial landmark predictor)
- alarm.wav (alert sound file)

## Code Structure

### Backend Components

**FastAPI Setup**
```python
app = FastAPI()
static_dir = "static"
```
The application initializes FastAPI and sets up a static directory for serving files.

**DrowsinessDetector Class**
- **Initialization**: Sets up face detection models and tracking variables
- **Key Methods**:
  - `compute()`: Calculates distance between facial landmarks
  - `blinked()`: Determines eye state using facial landmarks
  - `process_frame()`: Main processing pipeline for video frames

**WebSocket Endpoint**
```python
@app.websocket("/ws/video")
async def video_feed(websocket: WebSocket)
```
Handles real-time video streaming and processing.

### Frontend Components

**HTML Structure**
- Responsive container design
- Video display element
- Status indicator
- Start/Stop button

**JavaScript Functions**
- `loadAlarmSound()`: Initializes audio context
- `playAlarm()`: Triggers alert sound
- `stopAlarm()`: Stops alert playback
- `startDetection()`: Initiates WebSocket connection and video processing

## Features

### Face Detection
- Real-time face tracking using dlib
- 68-point facial landmark detection
- Continuous monitoring of eye movements

### Drowsiness States
1. **Active**: Normal eye movement detected
2. **Drowsy**: Partial eye closure detected
3. **Sleeping**: Extended eye closure detected

### Alert System
- Visual status indicators
- Audio alerts for dangerous states
- Alert cooldown system (30 seconds)

## Implementation Details

### Face Processing Pipeline
1. Frame capture from webcam
2. Conversion to grayscale
3. Face detection
4. Facial landmark extraction
5. Eye state analysis
6. Status determination
7. Frame annotation

### WebSocket Communication
- Base64 encoded frame transmission
- Status updates
- Alert trigger signals

### Frontend Behavior
- Real-time video display
- Dynamic status updates
- Automatic reconnection on connection loss
- Responsive design for different screen sizes

## Error Handling
- Face detection failures
- WebSocket connection issues
- Frame processing errors
- Audio context initialization

## Security Considerations
- Local webcam access required
- WebSocket connection security
- Resource management for continuous streaming

## Performance Optimization
- Asynchronous frame processing
- Efficient frame encoding
- Alert cooldown mechanism
- Memory management for video capture

## Usage Instructions
1. Install required dependencies
2. Place required model files in correct directory
3. Run FastAPI server
4. Access through web browser
5. Click "Start Detection" to begin monitoring

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/27487766/e44312e5-491f-4c75-9307-1fc037aa58d6/paste.txt