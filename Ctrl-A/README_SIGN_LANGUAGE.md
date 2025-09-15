# Sign Language Recognition Integration

This document explains how to set up and use the integrated sign language recognition system that connects the existing `prediction.py` with the Ctrl-A platform.

## Overview

The sign language recognition system has been integrated to work with the existing `prediction.py` file, which contains a trained machine learning model for detecting sign language gestures. The integration provides:

- **Server-based Recognition**: A Flask server that runs the prediction.py functionality
- **WebSocket Communication**: Real-time communication between the server and web interface
- **Fallback Support**: Local camera processing if the server is unavailable
- **Cross-feature Integration**: Sign language input works across all Ctrl-A features

## Files Added/Modified

### New Files
- `sign_language_server.py` - Flask server that integrates with prediction.py
- `templates/sign_language.html` - Standalone sign language detection interface
- `run_sign_language_server.py` - Script to start the sign language server
- `admin_schemes.html` - Admin interface for managing welfare schemes

### Modified Files
- `sign_language.js` - Updated to integrate with prediction.py server
- `auth_server.py` - Added admin routes
- `dashboard.html` - Added admin panel access

## Setup Instructions

### 1. Prerequisites

Ensure you have the following files and dependencies:

```bash
# Required files
- model.p (trained sign language model)
- prediction.py (existing sign language detection code)

# Required Python packages
pip install flask flask-socketio opencv-python mediapipe numpy pillow
```

### 2. Start the Sign Language Server

```bash
# Navigate to the Ctrl-A directory
cd buildthon/Ctrl-A

# Run the sign language server
python run_sign_language_server.py
```

The server will start on `http://localhost:5001`

### 3. Start the Main Ctrl-A Server

```bash
# In a separate terminal, start the main server
python auth_server.py
```

The main server will start on `http://localhost:5000`

### 4. Start the Welfare Schemes Backend

```bash
# In another terminal, start the schemes backend
cd buildthon/gov-schemes-project
python src/main.py
```

The schemes backend will start on `http://localhost:8000`

## Usage

### Sign Language Detection

1. **Access the Interface**: Navigate to any feature page (welfare schemes, AI assistant, etc.)
2. **Start Detection**: Click the "Start Sign Language" button
3. **Make Gestures**: Use hand gestures in front of your camera
4. **View Results**: Detected characters will appear in the interface

### Admin Panel

1. **Access Admin**: From the dashboard, click "Admin Panel"
2. **Manage Schemes**: Add, edit, or delete welfare schemes
3. **View Statistics**: See scheme counts and coverage
4. **Populate Database**: Load default schemes into the system

## How It Works

### Server Integration

1. **Camera Access**: The server initializes OpenCV camera capture
2. **MediaPipe Processing**: Hand landmarks are detected using MediaPipe
3. **Model Prediction**: The trained model from `model.p` predicts characters
4. **WebSocket Communication**: Results are sent to the web interface in real-time

### Character Mapping

The system maps detected characters to commands:

```javascript
const commandMap = {
    'A': 'help',
    'B': 'music', 
    'C': 'camera',
    'D': 'legal',
    'E': 'schemes',
    'F': 'assistant',
    'G': 'tasks',
    'H': 'clear',
    // ... more mappings
};
```

### Fallback System

If the prediction.py server is unavailable:
- The system falls back to local camera processing
- Basic gesture detection using color-based region detection
- Mock detection for testing purposes

## API Endpoints

### Sign Language Server (Port 5001)

- `GET /` - Sign language detection interface
- `POST /api/start_detection` - Start sign language detection
- `POST /api/stop_detection` - Stop sign language detection
- `GET /api/get_text_buffer` - Get current text buffer
- `POST /api/clear_buffer` - Clear text buffer

### Main Server (Port 5000)

- `GET /admin_schemes` - Admin panel interface
- All existing Ctrl-A routes

### Schemes Backend (Port 8000)

- `GET /api/v1/schemes/search` - Search welfare schemes
- `GET /api/v1/admin/schemes` - List schemes (admin)
- `POST /api/v1/admin/schemes` - Create scheme (admin)
- `PUT /api/v1/admin/schemes/{id}` - Update scheme (admin)
- `DELETE /api/v1/admin/schemes/{id}` - Delete scheme (admin)

## Troubleshooting

### Common Issues

1. **Camera Not Working**
   - Check camera permissions in browser
   - Ensure no other applications are using the camera
   - Try refreshing the page

2. **Model Not Found**
   - Ensure `model.p` file exists in the Ctrl-A directory
   - Check file permissions

3. **Server Connection Failed**
   - Verify all servers are running on correct ports
   - Check firewall settings
   - Ensure no port conflicts

4. **Sign Language Not Detecting**
   - Ensure good lighting conditions
   - Keep hands visible in camera frame
   - Try different hand gestures
   - Check confidence thresholds in the code

### Debug Mode

Enable debug mode by setting `debug=True` in the server startup:

```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

## Configuration

### Confidence Thresholds

Adjust detection sensitivity in `sign_language_server.py`:

```python
CONFIDENCE_THRESHOLD = 0.65  # Global threshold
PER_CLASS_THRESHOLDS = {
    'C': 0.22,
    'D': 0.45,
    # ... adjust per character
}
```

### Camera Settings

Modify camera settings in `sign_language_server.py`:

```python
cap.set(cv2.CAP_PROP_EXPOSURE, -3)
cap.set(cv2.CAP_PROP_GAIN, 100)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 100)
```

## Security Notes

- The admin panel requires authentication
- API keys should be properly configured for production
- Camera access is only granted with user permission
- All data is processed locally (no external API calls for sign language)

## Future Enhancements

- **Improved Model**: Train on more diverse sign language data
- **Multi-language Support**: Support for different sign languages
- **Gesture Sequences**: Support for complex gesture combinations
- **Offline Mode**: Complete offline sign language processing
- **Custom Training**: Allow users to train custom gestures

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the console logs for error messages
3. Ensure all dependencies are properly installed
4. Verify all servers are running correctly
