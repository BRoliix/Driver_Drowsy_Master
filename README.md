# 🚗 Driver Drowsiness Detection System

A real-time AI-powered drowsiness detection system that monitors drivers through their camera and automatically sends SOS alerts when drowsiness is detected. Built with FastAPI, OpenCV, and deployed on Railway with PocketBase database integration.

## 🎯 Features

- **Real-time Face Detection**: Uses OpenCV Haar cascades for robust face detection
- **Eye Monitoring**: Tracks eye closure patterns to detect drowsiness
- **Automatic SOS Alerts**: Sends alerts with location data when drowsiness is detected
- **Audio Alarms**: Browser-based alarm sounds using Web Audio API
- **Cloud Database**: Stores alerts in PocketBase with local fallback
- **Responsive Web Interface**: Works on desktop and mobile browsers
- **Location Tracking**: Automatically captures and stores location information

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Browser       │    │   FastAPI        │    │   PocketBase    │
│   (Camera +     │◄──►│   Server         │◄──►│   Database      │
│    Display)     │    │   (AI Detection) │    │   (SOS Alerts)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                        │                        │
        ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ WebSocket       │    │ OpenCV +         │    │ Local Storage   │
│ Video Stream    │    │ Computer Vision  │    │ (Fallback)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with WebSocket support
- **OpenCV**: Computer vision library for face and eye detection
- **dlib** (optional): Advanced facial landmark detection
- **SciPy**: Scientific computing for eye aspect ratio calculations
- **Geopy**: Location services and geocoding
- **PocketBase Python Client**: Database integration

### Frontend
- **HTML5**: Modern web interface
- **JavaScript**: Camera access and WebSocket communication
- **Web Audio API**: Browser-based alarm system
- **WebRTC**: Real-time camera access via `getUserMedia()`

### Database & Deployment
- **PocketBase**: Cloud database for SOS alerts
- **Railway**: Cloud hosting platform
- **Git**: Version control and CI/CD

## 🚀 How It Works

### 1. Camera Access & Video Processing
```javascript
// Browser captures video from user's camera
stream = await navigator.mediaDevices.getUserMedia({ video: true });
// Sends frames via WebSocket to server for processing
ws.send(JSON.stringify({ frame: base64ImageData }));
```

### 2. AI Drowsiness Detection
```python
# Server processes each frame
def process_frame(frame):
    # 1. Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    # 3. Detect eyes within face region
    eyes = eye_cascade.detectMultiScale(face_region, 1.1, 5)
    
    # 4. Count drowsy frames
    if len(eyes) < 2:  # Eyes likely closed
        drowsy_frames += 1
    
    # 5. Trigger alert if threshold reached
    if drowsy_frames >= DROWSY_FRAME_THRESHOLD:
        raise_sos()  # Send SOS alert
```

### 3. SOS Alert System
```python
def raise_sos():
    # 1. Get current location
    location = get_current_location()  # IP-based geolocation
    
    # 2. Create alert data
    sos_data = {
        'details': 'Driver detected sleeping/drowsy',
        'status': 'NEW',
        'latitude': location['latitude'],
        'longitude': location['longitude'],
        'address': location['address']
    }
    
    # 3. Save to PocketBase (with local fallback)
    pb.collection('sos_alerts').create(sos_data)
```

### 4. Real-time Communication
```
Browser ◄─── WebSocket ────► FastAPI Server
   │                              │
   ├─ Sends camera frames         ├─ Processes with OpenCV
   ├─ Receives processed frames   ├─ Detects drowsiness
   ├─ Updates UI status           ├─ Triggers SOS alerts
   └─ Plays alarm sounds          └─ Saves to database
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- Modern web browser with camera access
- PocketBase account (or self-hosted instance)

### Local Development
```bash
# Clone the repository
git clone https://github.com/BRoliix/Driver_Drowsy_Master.git
cd Driver_Drowsy_Master

# Install dependencies
cd server
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your PocketBase credentials

# Run the server
python -m uvicorn driver_drowsiness:app --host 0.0.0.0 --port 8000 --reload

# Open browser
open http://localhost:8000
```

### Environment Variables
```bash
POCKETBASE_URL=https://your-instance.pockethost.io/
POCKETBASE_ADMIN_EMAIL=your-email@example.com
POCKETBASE_ADMIN_PASSWORD=your-password
```

## 🌐 Deployment

### Railway Deployment
This project is configured for one-click deployment on Railway:

1. **Push to GitHub** (already done)
2. **Connect to Railway**:
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway link
   railway deploy
   ```

3. **Set Environment Variables** in Railway dashboard:
   - `POCKETBASE_URL`
   - `POCKETBASE_ADMIN_EMAIL` 
   - `POCKETBASE_ADMIN_PASSWORD`

### Deployment Files
- **`Procfile`**: Railway start command
- **`requirements.txt`**: Python dependencies optimized for Railway
- **`railway.toml`**: Railway configuration
- **`.env`**: Environment variables (not committed)

## 🗄️ Database Schema

### PocketBase Collections

#### `sos_alerts` Collection
```json
{
  "id": "auto-generated",
  "taxiid": "string (optional)",
  "driverid": "string (optional)", 
  "details": "string (required)",
  "status": "string (required)",
  "actionedtime": "datetime",
  "latitude": "number",
  "longitude": "number", 
  "address": "string",
  "created": "datetime (auto)",
  "updated": "datetime (auto)"
}
```

#### API Rules (PocketBase Configuration)
```
List/Search rule: [empty] (public access)
View rule: [empty] (public access)
Create rule: [empty] (public access)
Update rule: @request.auth.id != "" (authenticated users)
Delete rule: @request.auth.id != "" (authenticated users)
```

### Local Storage Fallback
When PocketBase is unavailable, alerts are stored locally in JSON files:
- `local_data/sos_alerts.json`
- Automatic sync when connection restored

## 🎮 Usage

### Starting Detection
1. **Open the application** in your browser
2. **Click "Start Detection"** button
3. **Allow camera permissions** when prompted
4. **Position your face** in the camera view
5. **System will monitor** for drowsiness automatically

### Detection Process
- **Green rectangle**: Face detected successfully
- **Status "Active"**: Driver is alert
- **Status "DROWSY!"**: Drowsiness detected
- **Frame counter**: Shows drowsy frame count
- **Automatic alerts**: SOS sent after 8 consecutive drowsy frames

### SOS Alert Flow
```
Drowsiness Detected → Alarm Sound → SOS Alert → Database Save → Location Capture
                                        ↓
                              Emergency contacts notified
                              (future enhancement)
```

## 🔧 Configuration

### Detection Settings
```python
# In driver_drowsiness.py
DROWSY_FRAME_THRESHOLD = 8    # Frames before alert (adjustable)
ALERT_COOLDOWN = 30           # Seconds between alerts
EAR_THRESHOLD = 0.25          # Eye aspect ratio threshold (if using dlib)
```

### Camera Settings
```javascript
// In HTML template
const constraints = {
    video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        frameRate: { ideal: 30 }
    }
};
```

## 🚨 Alert System

### Detection Algorithm
1. **Face Detection**: OpenCV Haar cascades identify face region
2. **Eye Detection**: Searches for eyes within detected face
3. **Drowsiness Logic**: 
   - If < 2 eyes detected → likely closed
   - Count consecutive "drowsy" frames
   - Trigger alert at threshold (default: 8 frames ≈ 1 second)

### Alert Data
```json
{
  "details": "Driver detected sleeping/drowsy. Immediate attention required.",
  "status": "NEW",
  "actionedtime": "2025-10-15T18:42:28.310055",
  "latitude": 1.2959,
  "longitude": 103.7907,
  "address": "26A, Ayer Rajah Crescent, Singapore"
}
```

### Location Services
- **IP-based geolocation**: Uses `geocoder` library
- **Address resolution**: Reverse geocoding with Nominatim
- **Fallback location**: Default coordinates if services fail
- **Privacy**: Location only captured during alerts

## 🎵 Audio System

### Web Audio API Implementation
```javascript
function createBeepSound(frequency = 800, duration = 500) {
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.frequency.value = frequency;
    oscillator.type = 'sine';
    
    // Create alert sound
    oscillator.start();
    oscillator.stop(audioContext.currentTime + duration / 1000);
}
```

### Sound Features
- **Browser-compatible**: No external audio files needed
- **Customizable**: Adjustable frequency and duration
- **Non-blocking**: Doesn't interfere with detection
- **Auto-stop**: Stops when driver becomes alert

## 📊 Performance Optimizations

### Detection Performance
- **Frame processing**: ~30 FPS capability
- **CPU optimization**: Efficient OpenCV operations
- **Memory management**: Proper cleanup of video frames
- **Error handling**: Graceful fallback mechanisms

### Network Optimization  
- **WebSocket compression**: Efficient frame transmission
- **Base64 encoding**: Optimized image data transfer
- **Connection management**: Auto-reconnection on failures
- **Local caching**: Reduces database load

## 🔒 Security & Privacy

### Data Protection
- **Local processing**: AI detection runs on server-side
- **Minimal data**: Only essential alert information stored
- **No video recording**: Frames processed in real-time only
- **Secure transmission**: WebSocket connections

### Privacy Features
- **Camera access**: User must explicitly grant permission
- **Location**: Only captured during actual alerts
- **No tracking**: No persistent user identification
- **Data retention**: Configurable alert retention policies

## 🐛 Troubleshooting

### Common Issues

#### Camera Access Denied
```javascript
// Solution: Check browser permissions
navigator.permissions.query({name: 'camera'}).then(result => {
    console.log(result.state); // granted, denied, or prompt
});
```

#### WebSocket Connection Fails
```bash
# Check if server is running
curl -I http://localhost:8000

# Verify WebSocket endpoint
wscat -c ws://localhost:8000/ws/video
```

#### PocketBase Connection Issues
```python
# Test PocketBase connectivity
import requests
response = requests.get('https://your-instance.pockethost.io/api/health')
print(response.status_code)  # Should be 200
```

#### Detection Not Working
- **Check lighting**: Ensure adequate face illumination
- **Camera positioning**: Face should be clearly visible
- **Browser compatibility**: Use modern browsers (Chrome, Firefox, Safari)
- **Performance**: Close other applications to free CPU resources

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Monitoring & Analytics

### Available Metrics
- **Detection accuracy**: Frame processing success rate
- **Alert frequency**: Number of SOS alerts per session
- **Response time**: Time from detection to alert
- **System performance**: CPU and memory usage

### Logging
```python
# Server logs include:
print("🚨 DROWSY DETECTED!")           # Alert triggered
print("✅ SOS alert saved")            # Database success  
print("📍 Location data: {...}")       # Location capture
print("🔊 Audio context initialized")  # Sound system
```

## 🔮 Future Enhancements

### Planned Features
- [ ] **Machine Learning**: Advanced drowsiness detection with TensorFlow
- [ ] **Multi-user Support**: Driver profiles and personalized settings
- [ ] **Emergency Contacts**: Automatic SMS/email notifications
- [ ] **Dashboard**: Analytics and alert history
- [ ] **Mobile App**: Native iOS/Android applications
- [ ] **Fleet Management**: Multi-vehicle monitoring
- [ ] **Voice Alerts**: Text-to-speech warnings

### Technical Improvements
- [ ] **Edge Computing**: On-device AI processing
- [ ] **WebRTC**: Peer-to-peer video streaming
- [ ] **PWA**: Progressive Web App capabilities
- [ ] **Offline Support**: Local-first architecture
- [ ] **Advanced Analytics**: Fatigue pattern analysis

## 🤝 Contributing

### Development Setup
```bash
# Fork the repository
git clone https://github.com/your-username/Driver_Drowsy_Master.git
cd Driver_Drowsy_Master

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/

# Submit pull request
git push origin feature/your-feature-name
```

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use modern ES6+ features
- **Comments**: Document complex algorithms
- **Testing**: Add tests for new features

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

### Getting Help
- **Issues**: Report bugs on [GitHub Issues](https://github.com/BRoliix/Driver_Drowsy_Master/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/BRoliix/Driver_Drowsy_Master/discussions)
- **Documentation**: Check this README and code comments

### Contact
- **GitHub**: [@BRoliix](https://github.com/BRoliix)
- **Project**: [Driver_Drowsy_Master](https://github.com/BRoliix/Driver_Drowsy_Master)

## 🎉 Acknowledgments

- **OpenCV Community**: Computer vision algorithms
- **FastAPI**: Modern Python web framework
- **PocketBase**: Excellent database solution
- **Railway**: Seamless deployment platform
- **Contributors**: Everyone who helped improve this project

---

**⚠️ Important Safety Notice**: This system is designed to assist drivers but should not be relied upon as the sole safety measure. Always prioritize getting adequate rest and avoid driving when tired. This technology is supplementary to, not a replacement for, responsible driving practices.

**🚀 Live Demo**: [https://driverdrowsymaster-production.up.railway.app/](https://driverdrowsymaster-production.up.railway.app/)

Made with ❤️ for safer roads and better driver awareness.