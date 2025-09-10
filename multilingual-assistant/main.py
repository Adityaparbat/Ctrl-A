from stt import listen
from tts import speak

def run_assistant():
    while True:
        text = listen()
        if not text:
            continue

        print("🗣 You said:", text)

        if "exit" in text.lower():
            print("👋 Exiting assistant...")
            break

        speak(text)

if __name__ == "__main__":
    run_assistant()
