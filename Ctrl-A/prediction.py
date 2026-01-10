import pickle
import cv2
import mediapipe as mp
import numpy as np
from typing import Optional

# Load the model
try:
    with open('./model.p', 'rb') as file:
        model_dict = pickle.load(file)
    model = model_dict['model']
except FileNotFoundError:
    print("Error: The file './model.p' was not found.")
    exit()
except KeyError:
    print("Error: The key 'model' was not found in the pickle file.")
    exit()
repeat_cooldown_frames = 5  # frames to wait before accepting repeats
frames_since_last_char = repeat_cooldown_frames
# Open the video capture (Windows: CAP_DSHOW improves exposure/latency)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# Try setting a reasonable resolution
# Try setting higher exposure and gain after cap is opened
cap.set(cv2.CAP_PROP_EXPOSURE, -3)   # Try values from -7 (very bright) to -1 (auto). Experiment.
cap.set(cv2.CAP_PROP_GAIN, 100)      # Try range 0-255 (some webcams support higher gain)
cap.set(cv2.CAP_PROP_BRIGHTNESS, 100) # Range 0-255 usually, but varies
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Initialize MediaPipe components
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.3)

# Inference settings
CONFIDENCE_THRESHOLD = 0.65  # Only accept predictions above this probability

# Gesture-to-action mappings. Customize these to match your dataset labels.
# If your dataset has explicit classes named 'SPACE', 'BACKSPACE', 'DELETE',
# list them here. Alternatively, you can map single-letter classes (e.g., 'S')
# to actions.
ACTION_GESTURES = {
    'SPACE': 'SPACE',
    'BACKSPACE': 'BACKSPACE',
    'DELETE': 'DELETE',
    # Optional aliases if your dataset uses letters instead of words
    'S': 'SPACE',
    'B': 'BACKSPACE',
    'D': 'DELETE',
}

# Optional: per-class confidence thresholds. If a class is not listed here,
# the global CONFIDENCE_THRESHOLD is used. Adjust values based on validation.
# Example lowers thresholds for 'C' and 'D'.
PER_CLASS_THRESHOLDS = {
    # 'A': 0.70,
    'C': 0.22,
    'D': 0.45,
    'U': 0.40,
    'N':0.20,
    '2':0.50,
    '1':0.50,
    'I':0.30,
}

# Labels dictionary
labels_dict = {0: '1', 1: '2', 2: '3',3: '4',4: '5',5: '6',6: '7',7: '8',8: '9',9:'A',10:'B',11:'C',12:'D',13:'E',14:'F',15:'G',16:'H',17:'I',18:'J',19:'K',20:'L',21:'M',22:'N',23:'O',24:'P',25:'Q',26:'R',27:'S',28:'T',29:'U',30:'V',31:'W',32:'X',33:'Y',34:'Z'}

# State for text buffer and last action to prevent rapid repeats
last_predicted_character: Optional[str] = None
text_buffer = []
print("Predictions:")
BRIGHTNESS_BETA = 0  # 0-100 typical effective range for cv2.convertScaleAbs beta

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Apply simple brightness gain on the frame for display and processing
    if BRIGHTNESS_BETA != 0:
        frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=BRIGHTNESS_BETA)

    H, W, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        data_aux = []
        x_ = []
        y_ = []

        # Pair landmarks with handedness and sort Left, then Right (to match training)
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

        # Draw landmarks and compute per-hand features with per-hand normalization
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
            print("Warning: No landmarks detected.")
            continue
        # Zero-pad to two hands (84 features total)
        hand_feat_len = 21 * 2
        while len(per_hand_features) < 2:
            per_hand_features.append([0.0] * hand_feat_len)
        data_aux = per_hand_features[0] + per_hand_features[1]

        if len(data_aux) == 84: 
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) + 10
            y2 = int(max(y_) * H) + 10
            try:
                frames_since_last_char += 1
                # Perform prediction with probabilities
                proba = None
                predicted_character = "Unknown"
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
            if 'proba' in locals() and proba is not None:
                class_threshold = PER_CLASS_THRESHOLDS.get(predicted_character, CONFIDENCE_THRESHOLD)
                passed_threshold = proba >= class_threshold

            # Debug: show top 3 predictions for similar classes
            if 'proba' in locals() and proba is not None and 'proba_vec' in locals():
                top3_indices = np.argsort(proba_vec)[-3:][::-1]
                top3_chars = [labels_dict.get(int(idx), f"Unknown_{int(idx)}") for idx in top3_indices]
                top3_probs = [float(proba_vec[int(idx)]) for idx in top3_indices]
                debug_text = f"Top3: {', '.join([f'{char}({prob*100:.1f}%)' for char, prob in zip(top3_chars, top3_probs)])}"
                cv2.putText(frame, debug_text, (10, H - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)

            # Apply gesture mappings and update text buffer or append character
            if predicted_character != last_predicted_character and predicted_character != "Unknown" and passed_threshold:
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
                    print(predicted_character, end='', flush=True)
                last_predicted_character = predicted_character
                frames_since_last_char = 0

            # Draw results on frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            info_text = predicted_character
            if 'proba' in locals() and proba is not None:
                class_threshold = PER_CLASS_THRESHOLDS.get(predicted_character, CONFIDENCE_THRESHOLD)
                info_text = f"{predicted_character} {proba*100:.1f}% (th={class_threshold*100:.0f}%)"
            cv2.putText(frame, info_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2, cv2.LINE_AA)
        
    # On-screen display of current buffer (always show, centered at top)
    buffer_text = ''.join(text_buffer)
    display_text = buffer_text if buffer_text else ''
    (tw, th), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 2)
    x_pos = max(10, (W - tw) // 2)
    cv2.putText(frame, display_text, (x_pos, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2, cv2.LINE_AA)

    # Show current brightness level
    cv2.putText(frame, f"Brightness: +{BRIGHTNESS_BETA}", (10, H - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)

    # Display the frame
    cv2.imshow('frame', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('+') or key == ord('='):
        # Increase software brightness and try camera brightness if supported
        BRIGHTNESS_BETA = min(100, BRIGHTNESS_BETA + 5)
        cap.set(cv2.CAP_PROP_BRIGHTNESS, cap.get(cv2.CAP_PROP_BRIGHTNESS) + 0.05)
    elif key == ord(' '):
        text_buffer.append(' ')
    elif key == 8:  # Backspace key
        if text_buffer:
            text_buffer.pop()
    elif key == 127:  # Delete key
        text_buffer = []
    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Print the complete word from the current text buffer
final_word = ''.join(text_buffer)
print(f"\nComplete Word: {final_word}")
