import os
import tempfile
import subprocess
from typing import Tuple

from flask import Flask, request, jsonify
from flask_cors import CORS
import whisper


app = Flask(__name__)
CORS(app)

# Load Whisper model once (CPU-friendly). Change to "small"/"medium" for better accuracy.
WHISPER_MODEL = whisper.load_model("base")


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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)


