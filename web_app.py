from flask import Flask, render_template, Response, request, jsonify
import cv2
import threading
import time
import json
import numpy as np
from camera_capture import CameraCapture
from gesture_recognition import GestureRecognition
from text_to_speech import TextToSpeech

app = Flask(__name__)

# Global variables for shared state
camera = None
gesture_recognizer = None
tts = None
current_language = "english"
last_gesture = ""
last_speech_time = 0
speech_cooldown = 2

def initialize_components():
    """Initialize camera, gesture recognition, and TTS components"""
    global camera, gesture_recognizer, tts

    # Initialize camera immediately - try multiple indices for Docker compatibility
    try:
        # In Docker, camera might not be available, so we'll handle this gracefully
        camera = None
        print("Note: Camera initialization deferred until video feed is accessed")
        print("This allows the app to run in environments without camera access")
    except Exception as e:
        print(f"Camera initialization setup failed: {e}")
        camera = None

    gesture_recognizer = GestureRecognition()
    print("Gesture recognition initialized")

    tts = TextToSpeech()
    print("Text-to-speech initialized")

    return True

def get_camera():
    """Lazy camera initialization - only when actually needed"""
    global camera

    if camera is not None:
        return camera

    try:
        # Try different camera indices
        for camera_index in [0, 1, 2, -1]:
            try:
                camera = CameraCapture(camera_index)
                camera.start_capture()
                print(f"Camera initialized successfully with index {camera_index}")
                return camera
            except Exception as e:
                print(f"Failed to initialize camera with index {camera_index}: {e}")
                continue
        else:
            print("Warning: No camera found. Application will run without camera.")
            camera = None
            return None
    except Exception as e:
        print(f"Camera initialization failed: {e}")
        camera = None
        return None

def generate_frames():
    """Generate video frames for web streaming"""
    global last_gesture, last_speech_time

    while True:
        try:
            # Try to get camera if not initialized
            cam = get_camera()

            if cam is None:
                # Create a placeholder frame when no camera is available
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Camera Not Available", (50, 200),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 2)
                cv2.putText(frame, "Please check camera connection", (50, 250),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
                cv2.putText(frame, "Try refreshing the page", (50, 300),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 1)
            else:
                frame = cam.get_frame()

            gesture, frame_with_landmarks = gesture_recognizer.process_frame(frame)

            # Display gesture on frame
            cv2.putText(frame_with_landmarks, f"Gesture: {gesture}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.putText(frame_with_landmarks, f"Language: {current_language}",
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            # Speak gesture if it's different and enough time has passed
            current_time = time.time()
            if (gesture != last_gesture and
                gesture not in ["No model loaded", "Unknown gesture"] and
                current_time - last_speech_time > speech_cooldown):

                # Translate common gestures to Hindi if needed
                if current_language == 'hindi':
                    translations = {
                        'hello': 'नमस्ते',
                        'thank you': 'धन्यवाद',
                        'please': 'कृपया'
                    }
                    speech_text = translations.get(gesture.lower(), gesture)
                else:
                    speech_text = gesture

                print(f"Detected: {gesture}")
                tts.speak(f"This is {speech_text}")
                last_gesture = gesture
                last_speech_time = current_time

            # Encode frame for web streaming
            ret, buffer = cv2.imencode('.jpg', frame_with_landmarks)
            frame_bytes = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            time.sleep(0.1)  # Small delay to prevent overwhelming

        except Exception as e:
            print(f"Error generating frame: {e}")
            # Create error frame
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, f"Error: {str(e)}", (50, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            ret, buffer = cv2.imencode('.jpg', error_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(1)

@app.route('/')
def index():
    """Main web page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/set_language', methods=['POST'])
def set_language():
    """Set the language for speech output"""
    global current_language
    try:
        data = request.get_json()
        language = data.get('language', 'english')

        if language in ['english', 'hindi']:
            tts.set_language(language)
            current_language = language
            return jsonify({'success': True, 'language': language})
        else:
            return jsonify({'success': False, 'error': 'Invalid language'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status')
def get_status():
    """Get current application status"""
    # Check if camera is available by trying to get it
    cam = get_camera()
    camera_status = "available" if cam is not None else "not available"
    return jsonify({
        'language': current_language,
        'last_gesture': last_gesture,
        'available_languages': tts.get_available_languages() if tts else [],
        'camera_status': camera_status
    })

if __name__ == '__main__':
    success = initialize_components()
    if success:
        print("Starting Flask server...")
        print("Open your browser and go to: http://localhost:5000")
        print("API docs available at: http://localhost:5000/status")
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        print("Failed to initialize components. Check camera and dependencies.")