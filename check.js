const ws = new WebSocket('ws://localhost:8000/ws/video');
const videoElement = document.getElementById('video');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    videoElement.src = `data:image/jpeg;base64,${data.frame}`;
    console.log('Detection Status:', data.status);
};
