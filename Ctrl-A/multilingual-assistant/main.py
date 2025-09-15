from stt import listen
from tts import speak, speak_in_lang
from notifier import get_disability_type
import os
from accessibility import process_accessible

def run_assistant():

    try:
        while True:
            text = listen()
            if not text:
                continue

            print("🗣 You said:", text)

            if "exit" in text.lower():
                print("👋 Exiting assistant...")
                break

            preferred_lang = os.getenv("PREFERRED_LANGUAGE", "")
            result = process_accessible("voice", text, preferred_language=preferred_lang)
            if not result.get("ok"):
                print("⚠ Unable to process input")
                continue

            final_text = result.get("text") or ""
            audio_file = result.get("audio_file")
            lang_used = result.get("language") or ""

            print("♿ Accessible:", final_text)

            if get_disability_type() != "hearing":
                try:
                    speak_in_lang(final_text, lang_used)
                except Exception:
                    pass

            if audio_file:
                print(f"🔊 Saved audio: {audio_file}")
    except KeyboardInterrupt:
        print("\n👋 Exiting assistant...")

if __name__ == "__main__":
    run_assistant()
