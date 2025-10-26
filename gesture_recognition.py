import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model
import os

class GestureRecognition:
    def __init__(self, model_path=None):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Load the gesture recognition model
        self.model = None
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)

        # Define gesture labels
        self.labels = [
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
            'hello', 'thank you', 'please'
        ]

        # Add basic ISL signs (placeholder - would need actual training data)
        isl_signs = ['namaste', 'sorry', 'good', 'bad', 'eat', 'drink']
        self.labels.extend(isl_signs)

    def extract_hand_landmarks(self, image):
        """Extract hand landmarks from image using MediaPipe"""
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Process the image
        results = self.hands.process(image_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]  # Take first hand

            # Extract landmark coordinates
            landmarks = []
            for landmark in hand_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])

            return np.array(landmarks), results.multi_hand_landmarks[0]
        return None, None

    def predict_gesture(self, landmarks):
        """Predict gesture from landmarks using the trained model"""
        if self.model is None or landmarks is None:
            return "No model loaded"

        # Reshape for model input
        landmarks = landmarks.reshape(1, -1)

        # Make prediction
        predictions = self.model.predict(landmarks, verbose=0)
        predicted_class = np.argmax(predictions[0])
        confidence = predictions[0][predicted_class]

        # Return prediction only if confidence is high enough
        if confidence > 0.7:
            return self.labels[predicted_class]
        else:
            return "Unknown gesture"

    def draw_hand_landmarks(self, image, hand_landmarks):
        """Draw hand landmarks on the image"""
        if hand_landmarks:
            self.mp_draw.draw_landmarks(
                image,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
        return image

    def process_frame(self, frame):
        """Process a single frame and return gesture prediction"""
        landmarks, hand_landmarks = self.extract_hand_landmarks(frame)
        gesture = self.predict_gesture(landmarks)

        # Draw landmarks on frame
        frame_with_landmarks = self.draw_hand_landmarks(frame.copy(), hand_landmarks)

        return gesture, frame_with_landmarks