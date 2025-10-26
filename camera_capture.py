import cv2
import numpy as np

class CameraCapture:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.cap = None

    def start_capture(self):
        """Initialize camera capture"""
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera with index {self.camera_index}")

        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def get_frame(self):
        """Capture and return a single frame"""
        if self.cap is None:
            raise RuntimeError("Camera not initialized. Call start_capture() first.")

        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame")

        return frame

    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __del__(self):
        self.release()