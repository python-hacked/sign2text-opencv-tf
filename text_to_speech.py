import threading
import queue
import time

class TextToSpeech:
    def __init__(self):
        self.speech_queue = queue.Queue()
        self.is_speaking = False
        self.current_language = "english"

        # Mock TTS - just print instead of speaking
        # This allows the app to run without TTS dependencies
        print("Text-to-speech initialized (mock mode - will print instead of speak)")

        # Start speech processing thread
        self.speech_thread = threading.Thread(target=self._process_speech_queue, daemon=True)
        self.speech_thread.start()

    def set_language(self, language):
        """Set the language for speech output"""
        if language.lower() == 'english' or language.lower() == 'en':
            self.current_language = 'english'
            print("Language set to English")
        elif language.lower() == 'hindi' or language.lower() == 'hi':
            self.current_language = 'hindi'
            print("Language set to Hindi")
        else:
            print(f"Unsupported language: {language}")

    def speak(self, text):
        """Add text to speech queue"""
        self.speech_queue.put(text)

    def _process_speech_queue(self):
        """Process speech queue in background thread"""
        while True:
            try:
                text = self.speech_queue.get(timeout=1)
                self.is_speaking = True

                # Mock speech - just print with language indicator
                if self.current_language == 'hindi':
                    print(f"🔊 Speaking in Hindi: {text}")
                else:
                    print(f"🔊 Speaking in English: {text}")

                # Simulate speech duration
                time.sleep(1)

                self.is_speaking = False
                self.speech_queue.task_done()
            except queue.Empty:
                continue

    def stop_speaking(self):
        """Stop current speech"""
        print("Speech stopped")

    def get_available_languages(self):
        """Return list of available languages"""
        return ['English', 'Hindi']