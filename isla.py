import os
import cv2
import numpy as np
import pyttsx3
from keras.models import load_model
import mediapipe as mp
import time

# Initialize MediaPipe Hands and Text-to-Speech Engine
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.85, min_tracking_confidence=0.85)  # Increase confidence
mp_drawing = mp.solutions.drawing_utils
engine = pyttsx3.init()

# Adjust text-to-speech rate and volume for better pronunciation
engine.setProperty('rate', 150)  # Slower speech rate
engine.setProperty('volume', 1)  # Max volume

# Define a dictionary mapping ISL hand gestures to text
gesture_text = {
    "namaste": "Namaste",
    "thank_you": "Thank you",
    "sorry": "Sorry",
    "yes": "Yes",
    "no": "No",
    "help": "Help"
}

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to detect ISL gestures based on hand landmarks
def detect_isl_gesture(hand_landmarks):
    landmarks = np.array([[lm.x, lm.y, lm.z] for lm in hand_landmarks.landmark])

    # Define gesture detection logic for ISL (to be customized)
    # Example placeholders - replace with actual ISL gesture logic
    if (landmarks[4][1] < landmarks[3][1] and landmarks[8][1] < landmarks[5][1]):
        return "namaste"
    if (landmarks[8][1] < landmarks[5][1] and landmarks[4][1] < landmarks[0][1]):
        return "thank_you"
    return "unknown"

# Buffer to hold detected gestures
gesture_buffer = []
BUFFER_SIZE = 5  # Number of frames to confirm the gesture

# Define path to the ISL model
model_path = r'C:\Sign-Language-To-Text-and-Speech-Conversion\cnn8grps_rad1_model.h5'

# Check if the model file exists
if not os.path.isfile(model_path):
    raise FileNotFoundError(f"The file '{model_path}' does not exist.")

# Load the ISL model
model = load_model(model_path)

# Open the webcam
cap = cv2.VideoCapture(0)

# Set frame size for performance optimization
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

prev_time = 0

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Calculate FPS for performance monitoring
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # Convert the BGR frame to RGB and resize
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = hands.process(image)

    # Convert back to BGR
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Detect the gesture based on hand landmarks
            recognized_gesture = detect_isl_gesture(hand_landmarks)

            # Add the detected gesture to the buffer
            gesture_buffer.append(recognized_gesture)

            # Maintain buffer size
            if len(gesture_buffer) > BUFFER_SIZE:
                gesture_buffer.pop(0)

            # Confirm gesture if the buffer contains the same gesture consistently
            if gesture_buffer.count(recognized_gesture) > BUFFER_SIZE // 2:
                if recognized_gesture in gesture_text:
                    text = gesture_text[recognized_gesture]
                    print(f"Recognized Gesture: {text}")
                    speak(text)  # Convert recognized text to speech

    # Display the frame with FPS
    cv2.putText(image, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("ISL Gesture Recognition", image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
