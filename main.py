import cv2
import time
from camera_capture import CameraCapture
from gesture_recognition import GestureRecognition
from text_to_speech import TextToSpeech

def main():
    print("Sign2Text with Voice Output")
    print("===========================")

    # Initialize components
    try:
        camera = CameraCapture()
        camera.start_capture()
        print("Camera initialized successfully")
    except Exception as e:
        print(f"Failed to initialize camera: {e}")
        return

    # Initialize gesture recognition (without model for now - will show hand tracking)
    gesture_recognizer = GestureRecognition()
    print("Gesture recognition initialized (MediaPipe hand tracking active)")

    # Initialize text-to-speech
    tts = TextToSpeech()
    print("Text-to-speech initialized")

    # Language selection
    print("\nAvailable languages:")
    languages = tts.get_available_languages()
    for i, lang in enumerate(languages, 1):
        print(f"{i}. {lang}")

    while True:
        try:
            lang_choice = input("\nSelect language (1 for English, 2 for Hindi, or 'q' to quit): ").strip().lower()
            if lang_choice == 'q':
                break
            elif lang_choice == '1' or lang_choice == 'english':
                tts.set_language('english')
                break
            elif lang_choice == '2' or lang_choice == 'hindi':
                tts.set_language('hindi')
                break
            else:
                print("Invalid choice. Please try again.")
        except KeyboardInterrupt:
            break

    print("\nStarting sign detection...")
    print("Press 'q' to quit, 'l' to change language")

    # Variables for gesture tracking
    last_gesture = None
    last_speech_time = 0
    speech_cooldown = 2  # seconds between speech outputs

    try:
        while True:
            # Capture frame
            frame = camera.get_frame()

            # Process gesture
            gesture, frame_with_landmarks = gesture_recognizer.process_frame(frame)

            # Display gesture on frame
            cv2.putText(frame_with_landmarks, f"Gesture: {gesture}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Speak gesture if it's different and enough time has passed
            current_time = time.time()
            if (gesture != last_gesture and
                gesture not in ["No model loaded", "Unknown gesture"] and
                current_time - last_speech_time > speech_cooldown):

                # Translate common gestures to Hindi if needed
                if tts.hindi_voice and hasattr(tts, 'hindi_voice') and tts.engine.getProperty('voice') == tts.hindi_voice.id:
                    # Basic translations (would need more comprehensive translation system)
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

            # Show frame
            cv2.imshow('Sign2Text', frame_with_landmarks)

            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('l'):
                # Language change
                print("\nChange language:")
                for i, lang in enumerate(languages, 1):
                    print(f"{i}. {lang}")
                try:
                    lang_choice = input("Select language: ").strip()
                    if lang_choice == '1':
                        tts.set_language('english')
                    elif lang_choice == '2':
                        tts.set_language('hindi')
                except:
                    pass

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error during execution: {e}")
    finally:
        # Cleanup
        camera.release()
        cv2.destroyAllWindows()
        print("Application closed")

if __name__ == "__main__":
    main()