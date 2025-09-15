import os
import re
import json
from typing import Dict, Any, Optional
from openai import OpenAI

# Import Google Generative AI for Gemini
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# -------------------------
# CONFIG
# -------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # Optional OpenAI key
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # free-friendly model

# Gemini support - using Google's Generative AI library
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC-aPYZkYF-qWYFxeokzkiZW49t_8FfoqY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def _has_openai_key() -> bool:
    return bool(OPENAI_API_KEY and OPENAI_API_KEY.strip())

def _has_gemini_key() -> bool:
    return bool(GEMINI_API_KEY and GEMINI_API_KEY.strip())

# -------------------------
# OPENAI
# -------------------------
def openai_chat(messages: list, max_tokens: int = 256) -> str:
    if not _has_openai_key():
        raise RuntimeError("OpenAI API key not configured")
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"OpenAI Error: {e}")

# -------------------------
# GEMINI (using Google Generative AI)
# -------------------------
def gemini_chat(messages: list, max_tokens: int = 256) -> str:
    if not _has_gemini_key():
        raise RuntimeError("Gemini API key not configured")
    
    if genai is None:
        raise RuntimeError("Google Generative AI library not installed. Run: pip install google-generativeai")
    
    try:
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Get the model
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Convert messages to a single prompt for Gemini
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            text = msg.get("content", "")
            if role == "system":
                prompt += f"System: {text}\n\n"
            elif role == "assistant":
                prompt += f"Assistant: {text}\n\n"
            else:
                prompt += f"User: {text}\n\n"
        
        # Generate response
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.7,
            )
        )
        
        return response.text
    except Exception as e:
        raise RuntimeError(f"Gemini Error: {e}")

# -------------------------
# UNIFIED AI CHAT
# -------------------------
def llm_chat(messages: list, max_tokens: int = 256) -> str:
    # Try OpenAI first if available
    if _has_openai_key():
        try:
            print("[AI] Using OpenAI")
            return openai_chat(messages, max_tokens=max_tokens)
        except Exception as e:
            print(f"[AI] OpenAI failed: {e}")
    
    # Then try Gemini if available
    if _has_gemini_key():
        try:
            print("[AI] Using Gemini")
            return gemini_chat(messages, max_tokens=max_tokens)
        except Exception as e:
            print(f"[AI] Gemini failed: {e}")
    
    # Offline fallback
    return "I'm currently offline (no API keys configured). Please set OPENAI_API_KEY or GEMINI_API_KEY."

def ask_ai(prompt: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful accessibility assistant. You can help with setting reminders, answering questions, and providing information. If the user mentions setting alarms or reminders, help them with that. Respond in the same language as the user's input."},
        {"role": "user", "content": prompt},
    ]
    return llm_chat(messages, max_tokens=200)

# -------------------------
# INTENT PARSING + TIME NORMALIZATION
# -------------------------
def normalize_time_to_24h(text: str, allow_bare_hour: bool = True) -> Optional[str]:
    # Supports: "6 PM", "06:30 pm", "18:00", Hindi: "6 बजे", "शाम 6 बजे", "सुबह 7:30"
    text_lower = text.strip().lower()

    # Map Hindi dayparts to am/pm
    daypart = None
    if any(w in text_lower for w in ["सुबह", "सवेरे"]):
        daypart = "am"
    elif any(w in text_lower for w in ["दोपहर", "शाम", "रात"]):
        daypart = "pm"

    # 24h pattern first
    m24 = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", text_lower)
    if m24:
        hours = int(m24.group(1))
        minutes = int(m24.group(2))
        return f"{hours:02d}:{minutes:02d}"

    # 12h with am/pm
    m12 = re.search(r"\b(1[0-2]|0?\d)(?::([0-5]\d))?\s*(am|pm)\b", text_lower)
    if m12:
        hours = int(m12.group(1))
        minutes = int(m12.group(2) or 0)
        ampm = m12.group(3)
        if ampm == "pm" and hours != 12:
            hours += 12
        if ampm == "am" and hours == 12:
            hours = 0
        return f"{hours:02d}:{minutes:02d}"

    # Hindi-style: number with optional minutes and "बजे"
    m_hi = re.search(r"\b(1[0-2]|0?\d)(?::([0-5]\d))?\s*(बजे)?\b", text_lower)
    if m_hi:
        hours = int(m_hi.group(1))
        minutes = int(m_hi.group(2) or 0)
        if daypart == "pm" and hours != 12:
            hours += 12
        if daypart == "am" and hours == 12:
            hours = 0
        return f"{hours:02d}:{minutes:02d}"

    # Bare hour (last resort)
    if allow_bare_hour:
        m_bare = re.search(r"\b(1[0-2]|0?\d)\b", text_lower)
        if m_bare:
            hours = int(m_bare.group(1))
            if daypart == "pm" and hours != 12:
                hours += 12
            if daypart == "am" and hours == 12:
                hours = 0
            if 0 <= hours <= 23:
                return f"{hours:02d}:00"

    return None

def extract_intent(user_text: str) -> Dict[str, Any]:
    """Parse intent using AI if available; fallback heuristics otherwise.

    Returns compact JSON: { action, time, note, time_normalized }
    - action: set_reminder | unknown (extendable later)
    - time: preserves user phrasing if LLM returns it; optional
    - note: short description (use input text as fallback)
    - time_normalized: HH:MM if we can infer; otherwise None
    """
    system = (
        "You are an intent parser. Return ONLY compact JSON with keys: "
        "action, time, note. action is one of set_reminder, unknown. "
        "time should preserve the user's phrasing if present (e.g., '6 PM'). "
        "note is a short description. Do not add explanations."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]

    # Try AI-assisted parsing
    try:
        raw = llm_chat(messages, max_tokens=128)
    except Exception:
        raw = ""

    # Best-effort JSON extraction
    json_text = (raw or "").strip()
    start = json_text.find("{")
    end = json_text.rfind("}")
    if start != -1 and end != -1:
        json_text = json_text[start:end+1]

    data: Dict[str, Any]
    try:
        parsed = json.loads(json_text) if json_text else {}
        if isinstance(parsed, dict) and parsed:
            data = parsed
        else:
            raise ValueError("empty or non-object")
    except Exception:
        # Fallback: multilingual heuristic for reminders only
        text_l = user_text.lower()
        # Stricter keywords to avoid false positives from common words like "याद"
        reminder_keywords = [
            # English
            "remind me", "set a reminder", "set reminder", "make a reminder",
            # Hindi transliteration
            "yaad dilao", "yaad dilana", "reminder set karo", "remind karo",
            # Hindi script (phrases)
            "याद दिलाओ", "रिमाइंडर सेट", "रिमाइंडर लगाओ", "रिमाइंडर",
        ]
        is_reminder = any(k in text_l for k in reminder_keywords)
        data = {
            "action": "set_reminder" if is_reminder else "unknown",
            "time": None,
            "note": user_text,
        }

    # Normalize time if present or infer from text; do NOT default a time
    normalized = None
    # If LLM provided an explicit time field, respect and normalize it (allow bare hour)
    if isinstance(data.get("time"), str) and (data["time"] or "").strip():
        normalized = normalize_time_to_24h(str(data["time"]), allow_bare_hour=True)
    # Only infer time from user text when it's actually a reminder request.
    # This avoids accidental time extraction from general queries (e.g., "iPhone 15").
    if not normalized and (data.get("action") == "set_reminder"):
        normalized = normalize_time_to_24h(user_text, allow_bare_hour=False)

    data["time_normalized"] = normalized
    return data

# -------------------------
# TEXT-ONLY HANDLER
# -------------------------
def handle_text(user_text: str) -> Dict[str, Any]:
    intent = extract_intent(user_text)
    # Prefer user's phrasing for display, otherwise normalized
    display_time = None
    if isinstance(intent.get("time"), str) and intent["time"].strip():
        display_time = intent["time"].strip()
    elif intent.get("time_normalized"):
        display_time = intent["time_normalized"]

    if intent.get("action") == "set_reminder" and intent.get("time_normalized"):
        note = intent.get("note") or "Reminder"
        assistant_reply = f"Reminder set for {display_time} to {note}."
    else:
        # Best-effort reply even if models are offline
        try:
            assistant_reply = ask_ai(user_text)
        except Exception:
            assistant_reply = "I parsed your request but I'm offline."

    return {
        "intent": intent,
        "assistant_reply": assistant_reply,
    }

# -------------------------
# INPUT ADAPTERS (text-only surface)
# -------------------------
def handle_transcript(transcript: str) -> Dict[str, Any]:
    """Accepts speech-to-text transcript (voice) and processes as text."""
    return handle_text(transcript)

def handle_gesture_text(gesture_text: str) -> Dict[str, Any]:
    """Accepts gesture/sign-language recognized text and processes as text."""
    return handle_text(gesture_text)

def process_input(source: str, text_payload: str) -> Dict[str, Any]:
    """Unified entry point for multi-modal input.

    Supported sources (aliases included):
    - text:     plain text input
    - tts:      text-to-speech pipeline input (still text before speaking)
    - stt:      speech-to-text transcript
    - voice:    alias for stt
    - gesture:  gesture/sign-language recognized text
    """
    src = (source or "text").strip().lower()
    if src in ("stt", "voice"):
        return handle_transcript(text_payload)
    if src == "gesture":
        return handle_gesture_text(text_payload)
    # For text or tts (which is still text content at this stage), use text handler
    if src in ("text", "tts"):
        return handle_text(text_payload)
    # Fallback to text
    return handle_text(text_payload)

# -------------------------
# TEST
# -------------------------
if __name__ == "__main__":
    query = "Remind me to take my medicine at 6 PM."
    print("User:", query)
    result = handle_text(query)
    print("Intent:", result["intent"])
    print("AI:", result["assistant_reply"])