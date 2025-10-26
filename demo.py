import cv2
import time

def demo_camera():
    """Simple demo to test camera functionality"""
    print("Testing camera...")

    # Try to open camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera")
        return

    print("Camera opened successfully!")
    print("Press 'q' to quit")

    frame_count = 0
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture frame")
            break

        frame_count += 1

        # Add some text overlay
        fps = frame_count / (time.time() - start_time)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Camera Test - Press 'q' to quit", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Show frame
        cv2.imshow('Camera Demo', frame)

        # Check for quit key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Camera test completed")

def demo_tts():
    """Simple demo to test text-to-speech"""
    try:
        import pyttsx3
        print("Testing text-to-speech...")

        engine = pyttsx3.init()
        engine.say("Hello! This is a test of the text to speech system.")
        engine.say("नमस्ते! यह टेक्स्ट टू स्पीच सिस्टम का परीक्षण है।")
        engine.runAndWait()

        print("Text-to-speech test completed")
    except ImportError:
        print("pyttsx3 not installed. Install with: pip install pyttsx3")

if __name__ == "__main__":
    print("Sign2Text Demo")
    print("==============")

    choice = input("Choose demo:\n1. Camera test\n2. Text-to-speech test\n3. Both\nChoice: ")

    if choice == '1':
        demo_camera()
    elif choice == '2':
        demo_tts()
    elif choice == '3':
        demo_camera()
        demo_tts()
    else:
        print("Invalid choice")