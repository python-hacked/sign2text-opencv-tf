from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import cv2
import asyncio
import json
import time
from camera_capture import CameraCapture
from gesture_recognition import GestureRecognition
from text_to_speech import TextToSpeech

app = FastAPI(title="Sign2Text API", description="AI-powered sign language recognition with voice output")

# Global variables for shared state
camera = None
gesture_recognizer = None
tts = None
current_language = "english"
last_gesture = ""
last_speech_time = 0
speech_cooldown = 2

async def initialize_components():
    """Initialize camera, gesture recognition, and TTS components"""
    global camera, gesture_recognizer, tts

    try:
        camera = CameraCapture()
        camera.start_capture()
        print("Camera initialized")
    except Exception as e:
        print(f"Camera initialization failed: {e}")
        return False

    gesture_recognizer = GestureRecognition()
    print("Gesture recognition initialized")

    tts = TextToSpeech()
    print("Text-to-speech initialized")

    return True

async def generate_frames():
    """Generate video frames for web streaming"""
    global last_gesture, last_speech_time

    while True:
        try:
            frame = camera.get_frame()
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

            await asyncio.sleep(0.1)  # Small delay to prevent overwhelming

        except Exception as e:
            print(f"Error generating frame: {e}")
            break

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main web page"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign2Text - AI Sign Language Recognition</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 30px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            }
            h1 { text-align: center; margin-bottom: 10px; font-size: 2.5em; }
            .main-content { display: grid; grid-template-columns: 1fr 300px; gap: 30px; }
            .video-container { background: rgba(0, 0, 0, 0.3); border-radius: 15px; padding: 20px; text-align: center; }
            .video-container img { max-width: 100%; border-radius: 10px; }
            .controls { background: rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 20px; }
            .btn { padding: 12px 20px; border: none; border-radius: 25px; cursor: pointer; margin: 5px; font-size: 16px; }
            .btn-english { background: #2196F3; color: white; }
            .btn-hindi { background: #FF9800; color: white; }
            .status { background: rgba(0, 0, 0, 0.2); border-radius: 10px; padding: 15px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤟 Sign2Text</h1>
            <p style="text-align: center; margin-bottom: 30px;">AI-Powered Sign Language Recognition with Voice Output</p>

            <div class="main-content">
                <div class="video-container">
                    <h2>Live Camera Feed</h2>
                    <img src="/video_feed" alt="Live Camera Feed">
                </div>

                <div class="controls">
                    <h3>Language / भाषा:</h3>
                    <button class="btn btn-english" onclick="setLanguage('english')">English</button>
                    <button class="btn btn-hindi" onclick="setLanguage('hindi')">हिंदी</button>

                    <div class="status">
                        <p><strong>Current Language:</strong> <span id="current-language">English</span></p>
                        <p><strong>Last Detected:</strong> <span id="last-gesture">-</span></p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function setLanguage(language) {
                try {
                    const response = await fetch('/set_language', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ language: language })
                    });
                    const data = await response.json();
                    if (data.success) {
                        document.getElementById('current-language').textContent =
                            language === 'english' ? 'English' : 'हिंदी';
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            }

            setInterval(async () => {
                try {
                    const response = await fetch('/status');
                    const data = await response.json();
                    document.getElementById('current-language').textContent =
                        data.language === 'english' ? 'English' : 'हिंदी';
                    document.getElementById('last-gesture').textContent = data.last_gesture || '-';
                } catch (error) {
                    console.error('Error updating status:', error);
                }
            }, 1000);
        </script>
    </body>
    </html>
    """

@app.get("/video_feed")
async def video_feed():
    """Video streaming route"""
    return StreamingResponse(generate_frames(),
                           media_type='multipart/x-mixed-replace; boundary=frame')

@app.post("/set_language")
async def set_language(request: Request):
    """Set the language for speech output"""
    global current_language
    try:
        data = await request.json()
        language = data.get('language', 'english')

        if language in ['english', 'hindi']:
            tts.set_language(language)
            current_language = language
            return {"success": True, "language": language}
        else:
            raise HTTPException(status_code=400, detail="Invalid language")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/status")
async def get_status():
    """Get current application status"""
    return {
        "language": current_language,
        "last_gesture": last_gesture,
        "available_languages": tts.get_available_languages() if tts else []
    }

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    success = await initialize_components()
    if not success:
        print("Warning: Some components failed to initialize")

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    print("Open your browser and go to: http://localhost:8000")
    print("API docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)