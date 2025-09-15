from gtts import gTTS
from config import TTS_LANGUAGE
import tempfile
import os

# Use pydub to convert to WAV then play with winsound (more reliable on Windows)
try:
    from pydub import AudioSegment
    import winsound
except Exception:
    AudioSegment = None  # type: ignore
    winsound = None  # type: ignore


def speak(text: str) -> None:
    """Convert text to speech and play it using system audio (Windows-safe)."""
    try:
        tts = gTTS(text=text, lang=TTS_LANGUAGE)
        with tempfile.TemporaryDirectory() as tmpdir:
            mp3_path = os.path.join(tmpdir, "reply.mp3")
            wav_path = os.path.join(tmpdir, "reply.wav")
            tts.save(mp3_path)

            if AudioSegment is not None and winsound is not None:
                # Convert MP3 -> WAV for robust Windows playback
                try:
                    audio = AudioSegment.from_file(mp3_path)
                    audio.export(wav_path, format="wav")
                    winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
                    return
                except Exception:
                    pass

            # Fallback: try to open the MP3 with default OS handler
            try:
                os.startfile(mp3_path)  # type: ignore[attr-defined]
            except Exception:
                raise RuntimeError("No supported audio playback method available.")
    except Exception as e:
        print("⚠️ TTS Error:", e)


def synthesize_to_file(text: str, lang: str, out_path: str) -> str:
    """Synthesize speech to an MP3 file without playing it. Returns path.

    Falls back to TTS_LANGUAGE if provided lang fails.
    """
    if not text:
        raise ValueError("text is empty")
    target_lang = (lang or TTS_LANGUAGE)
    try:
        tts = gTTS(text=text, lang=target_lang)
    except Exception:
        tts = gTTS(text=text, lang=TTS_LANGUAGE)

    out_dir = os.path.dirname(out_path) or "."
    os.makedirs(out_dir, exist_ok=True)
    tts.save(out_path)
    return out_path


def speak_in_lang(text: str, lang: str) -> None:
    """Speak text in a specified language code, falling back to default."""
    try:
        override = lang or TTS_LANGUAGE
        tts = gTTS(text=text, lang=override)
        with tempfile.TemporaryDirectory() as tmpdir:
            mp3_path = os.path.join(tmpdir, "reply.mp3")
            wav_path = os.path.join(tmpdir, "reply.wav")
            tts.save(mp3_path)
            if AudioSegment is not None and winsound is not None:
                try:
                    audio = AudioSegment.from_file(mp3_path)
                    audio.export(wav_path, format="wav")
                    winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_NODEFAULT)
                    return
                except Exception:
                    pass
            try:
                os.startfile(mp3_path)  # type: ignore[attr-defined]
            except Exception:
                raise RuntimeError("No supported audio playback method available.")
    except Exception as e:
        print("⚠️ TTS Error:", e)