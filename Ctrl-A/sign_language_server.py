"""
Sign Language Recognition Server

This server provides a web interface for the existing prediction.py sign language detection.
It runs the OpenCV-based sign language recognition and provides results via WebSocket.
"""

import cv2
import mediapipe as mp
import numpy as np
import pickle
import threading
import time
import json
from flask import Flask, render_template, request, jsonify, Response
from flask_socketio import SocketIO, emit
import base64
from io import BytesIO
from PIL import Image

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sign_language_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for sign language detection
is_detection_active = False
detection_thread = None
last_predicted_character = None
text_buffer = []
frames_since_last_char = 0
repeat_cooldown_frames = 5

# Load the model (try multiple common locations)
def _load_model():
    candidate_paths = [
        './model.p',
        os.path.join(os.path.dirname(__file__), 'model.p'),
        os.path.join(os.path.dirname(__file__), 'models', 'model.p'),
        os.path.join(os.path.dirname(__file__), '..', 'model.p'),
    ]
    for path in candidate_paths:
        try:
            with open(path, 'rb') as file:
                model_dict = pickle.load(file)
            print(f"Loaded model from: {os.path.abspath(path)}")
            return model_dict.get('model')
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"Error loading model from {path}: {e}")
            continue
    print("Error: model.p not found. Expected at one of: \n - " + "\n - ".join(candidate_paths))
    return None

model = _load_model()

# Initialize MediaPipe components
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.3)

# Visual overlay config
BRIGHTNESS_BETA = 0  # software brightness boost (0 means off)

# Inference settings
CONFIDENCE_THRESHOLD = 0.65

# Gesture-to-action mappings
ACTION_GESTURES = {
    'SPACE': 'SPACE',
    'BACKSPACE': 'BACKSPACE',
    'DELETE': 'DELETE',
    'S': 'SPACE',
    'B': 'BACKSPACE',
    'D': 'DELETE',
}

# Per-class confidence thresholds
PER_CLASS_THRESHOLDS = {
    'C': 0.22,
    'D': 0.45,
    'U': 0.40,
    'N': 0.20,
    '2': 0.50,
    '1': 0.50,
    'I': 0.30,
}

# Labels dictionary
labels_dict = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8', 8: '9', 9: 'A', 10: 'B', 11: 'C', 12: 'D', 13: 'E', 14: 'F', 15: 'G', 16: 'H', 17: 'I', 18: 'J', 19: 'K', 20: 'L', 21: 'M', 22: 'N', 23: 'O', 24: 'P', 25: 'Q', 26: 'R', 27: 'S', 28: 'T', 29: 'U', 30: 'V', 31: 'W', 32: 'X', 33: 'Y', 34: 'Z'}

def process_frame(frame):
    """Process a single frame for sign language detection."""
    global last_predicted_character, text_buffer, frames_since_last_char
    
    if model is None:
        return None, "Model not loaded"
    
    # Apply optional brightness boost for visibility
    if BRIGHTNESS_BETA != 0:
        frame[:] = cv2.convertScaleAbs(frame, alpha=1.0, beta=BRIGHTNESS_BETA)

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        data_aux = []
        x_ = []
        y_ = []

        # Pair landmarks with handedness and sort Left, then Right
        paired = []
        handedness_list = getattr(results, 'multi_handedness', None)
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            label = None
            if handedness_list and idx < len(handedness_list):
                try:
                    label = handedness_list[idx].classification[0].label
                except Exception:
                    label = None
            paired.append((label, hand_landmarks))

        def sort_key(item):
            label, _ = item
            if label == 'Left':
                return 0
            if label == 'Right':
                return 1
            return 2
        paired.sort(key=sort_key)

        # Draw landmarks and compute per-hand features
        per_hand_features = []
        for _, hand_landmarks in paired[:2]:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            xs = [lm.x for lm in hand_landmarks.landmark]
            ys = [lm.y for lm in hand_landmarks.landmark]
            if xs and ys:
                x_.extend(xs)
                y_.extend(ys)
                min_x = min(xs)
                min_y = min(ys)
                feats = []
                for lm in hand_landmarks.landmark:
                    feats.append(lm.x - min_x)
                    feats.append(lm.y - min_y)
                per_hand_features.append(feats)

        # Handle empty lists
        if not x_ or not y_:
            return None, "No landmarks detected"

        # Zero-pad to two hands (84 features total)
        hand_feat_len = 21 * 2
        while len(per_hand_features) < 2:
            per_hand_features.append([0.0] * hand_feat_len)
        data_aux = per_hand_features[0] + per_hand_features[1]

        if len(data_aux) == 84:
            try:
                frames_since_last_char += 1
                # Perform prediction with probabilities
                proba = None
                proba_vec = None
                predicted_character = "Unknown"
                predicted_label = None
                
                if hasattr(model, 'predict_proba'):
                    proba_all = model.predict_proba([np.asarray(data_aux)])
                    if isinstance(proba_all, list):
                        proba_all = proba_all[0]
                    proba_vec = np.asarray(proba_all).ravel()
                    top_idx = int(np.argmax(proba_vec))
                    proba = float(np.max(proba_vec))
                    predicted_label = top_idx
                else:
                    prediction = model.predict([np.asarray(data_aux)])
                    predicted_label = int(prediction[0])
                
                if predicted_label in labels_dict:
                    predicted_character = labels_dict[predicted_label]
            except Exception as e:
                print(f"Error during prediction: {e}")
                predicted_character = "Unknown"

            # Confidence thresholding
            passed_threshold = True
            if proba is not None:
                class_threshold = PER_CLASS_THRESHOLDS.get(predicted_character, CONFIDENCE_THRESHOLD)
                passed_threshold = proba >= class_threshold

            # Determine bounding box for overlay
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) + 10
            y2 = int(max(y_) * H) + 10

            # Overlay rectangle and main info
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            info_text = predicted_character
            if proba is not None:
                class_threshold = PER_CLASS_THRESHOLDS.get(predicted_character, CONFIDENCE_THRESHOLD)
                info_text = f"{predicted_character} {proba*100:.1f}% (th={class_threshold*100:.0f}%)"
            cv2.putText(frame, info_text, (x1, max(30, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2, cv2.LINE_AA)

            # Top-3 predictions debug overlay
            top3_chars = []
            top3_probs = []
            if proba_vec is not None:
                top3_indices = np.argsort(proba_vec)[-3:][::-1]
                top3_chars = [labels_dict.get(int(idx), f"?{int(idx)}") for idx in top3_indices]
                top3_probs = [float(proba_vec[int(idx)]) for idx in top3_indices]
                debug_text = ", ".join([f"{c}({p*100:.1f}%)" for c, p in zip(top3_chars, top3_probs)])
                cv2.putText(frame, f"Top3: {debug_text}", (10, H - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)

            # Update text buffer and de-bounce
            if (predicted_character != "Unknown" and 
                passed_threshold and 
                (predicted_character != last_predicted_character or frames_since_last_char >= repeat_cooldown_frames)):

                action = ACTION_GESTURES.get(predicted_character)
                if action == 'SPACE':
                    text_buffer.append(' ')
                elif action == 'BACKSPACE':
                    if text_buffer:
                        text_buffer.pop()
                elif action == 'DELETE':
                    text_buffer = []
                else:
                    text_buffer.append(predicted_character)

                last_predicted_character = predicted_character
                frames_since_last_char = 0

                # Send the detected character via WebSocket including top-3
                socketio.emit('sign_detected', {
                    'character': predicted_character,
                    'confidence': proba,
                    'text_buffer': ''.join(text_buffer),
                    'action': action,
                    'top3': [{'char': c, 'prob': p} for c, p in zip(top3_chars, top3_probs)]
                })

            # Always overlay current buffer on top center
            buffer_text = ''.join(text_buffer)
            (tw, th), _ = cv2.getTextSize(buffer_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
            x_pos = max(10, (W - tw) // 2)
            cv2.putText(frame, buffer_text, (x_pos, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2, cv2.LINE_AA)

            return predicted_character, proba

    return None, None

def detection_loop():
    """Main detection loop that runs in a separate thread."""
    global is_detection_active
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_EXPOSURE, -3)
    cap.set(cv2.CAP_PROP_GAIN, 100)
    cap.set(cv2.CAP_PROP_BRIGHTNESS, 100)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        socketio.emit('error', {'message': 'Could not open video capture'})
        return
    
    socketio.emit('status', {'message': 'Camera started successfully'})
    
    global latest_frame
    while is_detection_active:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame
        character, confidence = process_frame(frame)

        # Keep a copy for streaming
        try:
            latest_frame = frame.copy()
        except Exception:
            latest_frame = frame
        
        # Send frame data (optional - for debugging)
        if character:
            print(f"Detected: {character} (confidence: {confidence})")
        
        time.sleep(0.1)  # Small delay to prevent overwhelming
    
    cap.release()
    socketio.emit('status', {'message': 'Camera stopped'})


# ===== Live MJPEG stream to mirror prediction.py window =====
latest_frame = None

def _mjpeg_generator():
    global latest_frame
    fps_sleep = 0.03  # ~30 FPS cap for the stream
    import time
    while True:
        if latest_frame is None:
            time.sleep(0.05)
            continue
        try:
            ok, jpg = cv2.imencode('.jpg', latest_frame)
            if not ok:
                time.sleep(0.03)
                continue
            frame_bytes = jpg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(fps_sleep)
        except GeneratorExit:
            break
        except Exception:
            time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    """MJPEG video stream showing the live camera with landmarks drawn."""
    return Response(_mjpeg_generator(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    """Serve the sign language detection interface."""
    return render_template('sign_language.html')

@app.route('/api/start_detection', methods=['POST'])
def start_detection():
    """Start sign language detection."""
    global is_detection_active, detection_thread, text_buffer
    
    if is_detection_active:
        return jsonify({'success': False, 'message': 'Detection already active'})
    
    if model is None:
        return jsonify({'success': False, 'message': 'Model not loaded'})
    
    is_detection_active = True
    text_buffer = []
    detection_thread = threading.Thread(target=detection_loop)
    detection_thread.daemon = True
    detection_thread.start()
    
    return jsonify({'success': True, 'message': 'Detection started'})

@app.route('/api/stop_detection', methods=['POST'])
def stop_detection():
    """Stop sign language detection."""
    global is_detection_active
    
    is_detection_active = False
    
    return jsonify({'success': True, 'message': 'Detection stopped'})

@app.route('/api/get_text_buffer', methods=['GET'])
def get_text_buffer():
    """Get current text buffer."""
    return jsonify({'text_buffer': ''.join(text_buffer)})

@app.route('/api/clear_buffer', methods=['POST'])
def clear_buffer():
    """Clear the text buffer."""
    global text_buffer
    text_buffer = []
    return jsonify({'success': True, 'message': 'Buffer cleared'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('status', {'message': 'Connected to sign language server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5001)
