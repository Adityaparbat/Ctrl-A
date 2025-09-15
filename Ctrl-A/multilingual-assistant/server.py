import os
import tempfile
import subprocess
from typing import Tuple

from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper
import sys
import os as _os

# Allow importing gpt.py from project root
PROJECT_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

import gpt  # type: ignore
from scheduler import ReminderScheduler
from ics_calendar import write_event_ics
from notifier import notify


app = Flask(__name__)
CORS(app)

# Load Whisper model once (CPU-friendly). Change to "small"/"medium" for better accuracy.
WHISPER_MODEL = whisper.load_model("base")

# Shared in-process scheduler for web requests
web_scheduler = ReminderScheduler(on_reminder=lambda note: notify(f"{note}"))


def _convert_to_wav(src_path: str) -> Tuple[str, bool]:
    """Convert an audio file to 16k mono WAV using ffmpeg if needed.

    Returns (wav_path, created_temp) where created_temp indicates whether a new file was created.
    """
    if src_path.lower().endswith(".wav"):
        return src_path, False

    wav_fd, wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(wav_fd)
    # Requires ffmpeg in PATH
    cmd = [
        "ffmpeg", "-y", "-i", src_path,
        "-ac", "1", "-ar", "16000", wav_path,
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return wav_path, True


@app.route("/transcribe", methods=["POST"])
def transcribe():
    """Accepts multipart/form-data with field 'audio'. Returns JSON transcription.

    If 'language' is provided and not 'auto', it hints Whisper; otherwise auto-detect.
    """
    if "audio" not in request.files:
        return jsonify({"error": "Missing file field 'audio'"}), 400

    language = request.form.get("language", "auto")

    file = request.files["audio"]
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=os.path.splitext(file.filename or "audio")[1] or ".webm")
    os.close(tmp_fd)
    file.save(tmp_path)

    try:
        wav_path, created = _convert_to_wav(tmp_path)
        if language and language != "auto":
            result = WHISPER_MODEL.transcribe(wav_path, language=language, task="transcribe")
        else:
            result = WHISPER_MODEL.transcribe(wav_path, task="transcribe")

        text = (result or {}).get("text", "").strip()
        detected = (result or {}).get("language")
        return jsonify({
            "text": text,
            "language": detected or language or "auto",
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        try:
            if created:
                os.remove(wav_path)
        except Exception:
            pass
        try:
            os.remove(tmp_path)
        except Exception:
            pass


@app.route("/process", methods=["POST"])
def process():
    """Process text via GPT intent parser and schedule reminders.

    Expects JSON: { "source": "text|stt|tts|gesture", "text": "..." }
    Returns JSON with assistant_reply, intent, and scheduling info.
    """
    try:
        payload = request.get_json(force=True, silent=False) or {}
    except Exception as e:
        return jsonify({"error": f"Invalid JSON: {e}"}), 400

    source = (payload.get("source") or "text").strip().lower()
    text = (payload.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Missing 'text'"}), 400

    try:
        result = gpt.process_input(source, text)
        intent = result.get("intent", {})
        assistant_reply = result.get("assistant_reply") or ""

        scheduled = False
        when_iso = None
        ics_path = None

        if intent.get("action") == "set_reminder" and intent.get("time_normalized"):
            note = intent.get("note") or "Reminder"
            time_hhmm = intent.get("time_normalized")
            run_at = web_scheduler.add_reminder(time_hhmm, note)
            when_iso = run_at.isoformat()
            try:
                ics_path = write_event_ics(title=note, start=run_at)
            except Exception:
                ics_path = None
            scheduled = True
            if not assistant_reply:
                assistant_reply = f"Reminder set for {run_at.strftime('%I:%M %p')} to {note}."

        return jsonify({
            "assistant_reply": assistant_reply,
            "intent": intent,
            "scheduled": scheduled,
            "when": when_iso,
            "ics_path": ics_path,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)


