# Ctrl‑A Accessibility Suite (Buildthon openai x nxtwave)

A multi‑app accessibility platform that provides:
- AI Assistant (web) with LLM integration, TTS, and sign‑language hooks
- Camera Navigation (object/text detection, narration)
- Government Schemes discovery (RAG search)
- Multilingual assistant services and utilities
- Offline Chatbot (Ollama-based) with text/voice/sign inputs

This repository contains multiple Python/JS apps that work together under a common UI.

## Repository Layout

- `Ctrl-A/` – Main Flask app that serves dashboard, auth, AI assistant UI, and mounts sub‑apps
  - `auth_server.py` – main server (port 5000)
  - `templates/`, HTML files for pages
  - `half1/` – camera navigation service mounted at `/navigation/` from the main server (also standalone at 5001)
  - `multilingual-assistant/` – STT/TTS/assistant utilities and web endpoints
- `gov-schemes-project/` – FastAPI service and static UI for welfare schemes search (RAG)
- `offline_chatbot/` – Static offline chatbot UI that talks to a local Ollama server
- `gpt.py` – Unified LLM integration (OpenAI + Gemini) and intent parsing helpers

## Requirements

- Python 3.11
- Node not required (static frontends)
- FFmpeg (for audio streaming/transcoding)
- yt-dlp (YouTube audio extraction)
- Optional LLM keys:
  - `OPENAI_API_KEY` (for ChatGPT‑like responses)
  - `GEMINI_API_KEY` (alternative)
- Optional: Ollama (for offline chatbot): https://ollama.com

## Quick Start

Open a terminal in `buildthon/Ctrl-A` and create a virtualenv (recommended):

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Install multimedia tools:

```powershell
pip install yt-dlp
# Install ffmpeg (choose one)
choco install ffmpeg -y
# or
winget install --id Gyan.FFmpeg -e
```

Run the main server (Dashboard @ http://localhost:5000):

```powershell
python run_server.py
```

You should see routes:
- Dashboard: `http://localhost:5000/dashboard`
- AI Assistant: `http://localhost:5000/ai_assistant`
- Daily Tasks (music/reminders): `http://localhost:5000/daily_tasks`
- Camera Navigation: `http://localhost:5000/navigation/` (mounts the 5001 app)
- Offline Chatbot: `http://localhost:5000/offline`
- Government Schemes UI: `http://localhost:8001/` (when that service is running)

## Services

### 1) Main Server (port 5000)
Run from `Ctrl-A/`:
```powershell
python run_server.py
```
Provides authentication, dashboard, AI assistant, daily tasks, and mounts camera navigation at `/navigation`.

Key endpoints used by UI:
- `POST /api/ai-assistant` – Chat endpoint using `gpt.py` (OpenAI/Gemini) with history + TTS
- `POST /api/tts` – gTTS endpoint for audio replies
- `POST /api/play-music` – yt-dlp search; returns proxied and MP3 stream URLs
- `GET /api/stream` – CORS/range proxy for remote audio
- `GET /api/stream-mp3` – ffmpeg MP3 remux/transcode stream
- `POST /api/download-music` – fallback download + convert to local MP3

Environment overrides:
- `FFMPEG_BIN` – path to ffmpeg binary (if not on PATH)
- `OPENAI_API_KEY`, `OPENAI_MODEL` (default `gpt-4o-mini`)
- `GEMINI_API_KEY`, `GEMINI_MODEL` (default `gemini-1.5-flash`)

### 2) Camera Navigation (port 5001)
Standalone app in `Ctrl-A/half1/` (also mounted at `/navigation/`):
```powershell
cd Ctrl-A/half1
python app.py
```
UI: `http://localhost:5001/` (Back to Dashboard link included)

### 3) Government Schemes (port 8001)
From `gov-schemes-project/`:
```powershell
# Windows
setup.bat
run.bat
# Or manually
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run_sign_language_server.py
```
UI: `http://127.0.0.1:8001/` (Back to Dashboard link included)

### 4) Offline Chatbot (Ollama)
UI lives at `http://localhost:5000/offline`. It calls a local Ollama server.

Start Ollama and pull a model (example `gpt-oss`):
```powershell
ollama serve
ollama pull gpt-oss
```
If memory is limited, pick a smaller model (e.g., `llama3.2:1b` or similar) and update the model name inside `offline_chatbot/index.html` inline script.

## AI Assistant Behavior

- Uses `gpt.py` to call OpenAI or Gemini, with graceful offline fallbacks
- Conversation history is preserved by the page and sent with each request
- TTS uses gTTS; language is mapped from UI selection
- For music, streams are proxied and remuxed to MP3 where needed; a download fallback exists

## Sign Language Integration

- Buttons in the assistant and offline chatbot open `http://localhost:5001/` for sign language/camera features
- Both pages listen for `postMessage({ type: 'sign_result', text })` and submit that text automatically

## Environment Variables (optional)

Set via PowerShell and restart your shell:
```powershell
setx OPENAI_API_KEY "sk-..."
setx GEMINI_API_KEY "..."
setx FFMPEG_BIN "C:\\Path\\to\\ffmpeg.exe"
```

## Troubleshooting

- Music playback shows “Playback error”
  - Ensure `yt-dlp` is installed and `ffmpeg -version` works
  - The server logs include `[stream]`, `[stream-mp3]`, or `[download-music]` messages; copy any error for debugging
  - Network/CDN issues: try a different query; the download fallback should still work
- Offline chatbot TTS is silent
  - Browsers may block autoplay; press Send once to allow speech
- Sign language input not working
  - Ensure the camera/sign server at 5001 is running and the page has permission to open it
- OpenAI/Gemini offline
  - Assistant will provide generic helpful responses and direction links

## Security & Privacy

- This demo app stores minimal state client-side; no production‑grade auth for admin endpoints unless configured in the gov‑schemes service
- Do not store secrets in code. Use env vars.

## Development Notes

- Python formatting/typing is kept simple; match local style
- When editing static HTML/CSS/JS, perform hard refresh (Ctrl+F5) due to caching

## License

For hackathon/demo use. Adapt for production with appropriate auth, rate‑limits, and data protection.
