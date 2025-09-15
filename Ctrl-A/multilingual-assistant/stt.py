import tempfile
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from config import STT_LANGUAGE

recognizer = sr.Recognizer()

def listen(duration_seconds: int = 5, sample_rate: int = 16000) -> str:
    """Record audio from default microphone and return transcribed text.

    Falls back with empty string on errors.
    """
    print(f"🎤 Speak in {STT_LANGUAGE} ...")
    try:
        recording = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        sf.write(wav_path, recording, sample_rate)

        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language=STT_LANGUAGE)
        return text
    except sr.UnknownValueError:
        print("⚠ Could not understand audio")
        return ""
    except sr.RequestError as e:
        print("⚠ API error:", e)
        return ""
    except Exception as e:
        print("⚠ Recording error:", e)
        return ""