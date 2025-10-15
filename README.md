# Driver Drowsiness Detection System

A real-time driver drowsiness detection system using computer vision and facial landmark detection.

## Features

- 🎥 Real-time video processing through webcam
- 👁️ Eye Aspect Ratio (EAR) based drowsiness detection
- 🚨 Automatic SOS alerts when drowsiness detected
- 📍 GPS location tracking for alerts
- 🌐 Web-based interface with live video streaming
- 📊 PocketBase database integration
- 🔔 Audio alarms for immediate driver notification

## Tech Stack

- **Backend**: FastAPI with WebSocket support
- **Computer Vision**: OpenCV, dlib
- **Database**: PocketBase
- **Frontend**: HTML5, JavaScript, WebRTC
- **Deployment**: Railway/Render ready

## Quick Start

### Local Development

1. **Clone and setup:**
```bash
git clone https://github.com/BRoliix/Driver_Drowsy_Master.git
cd Driver_Drowsy_Master/server
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your PocketBase credentials
```

4. **Run the application:**
```bash
uvicorn driver_drowsiness:app --host 0.0.0.0 --port 8000
```

5. **Access the application:**
- Open `http://localhost:8000` in your browser
- Allow camera permissions when prompted

### Deployment

This application is configured for deployment on Railway, Render, or similar platforms.

## Configuration

The system requires the following environment variables:

```env
POCKETBASE_URL=your_pocketbase_url
POCKETBASE_ADMIN_EMAIL=your_admin_email  
POCKETBASE_ADMIN_PASSWORD=your_admin_password
```

## How It Works

1. **Video Capture**: Captures video stream from user's webcam
2. **Face Detection**: Uses dlib's face detector to locate faces
3. **Landmark Detection**: Identifies 68 facial landmarks
4. **EAR Calculation**: Computes Eye Aspect Ratio to detect closed eyes
5. **Drowsiness Detection**: Triggers alert if eyes closed for >8 frames
6. **SOS System**: Automatically creates SOS alerts with GPS location
7. **Real-time Alerts**: Provides audio and visual warnings

## API Endpoints

- `GET /` - Main web interface
- `WebSocket /ws/video` - Real-time video streaming
- `GET /static/*` - Static files (CSS, JS, audio)

## Database Schema

### SOS Alerts Collection
- `taxiid` - Taxi identifier
- `driverid` - Driver identifier
- `details` - Alert description  
- `status` - Alert status (NEW/ACTIONED)
- `latitude/longitude` - GPS coordinates
- `address` - Location address
- `createdtime` - Alert timestamp

## Security Features

- Admin authentication for database access
- Secure WebSocket connections
- Environment-based configuration
- Input validation and error handling

## Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+  
- ✅ Safari 11+
- ✅ Edge 79+

## Performance

- Real-time processing at 30 FPS
- Low latency WebSocket streaming
- Optimized computer vision algorithms
- Minimal resource usage

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email rohilsagar2003@gmail.com or create an issue on GitHub.

---

**⚠️ Important**: This system is designed for demonstration and research purposes. For production use in vehicles, ensure compliance with local regulations and safety standards.