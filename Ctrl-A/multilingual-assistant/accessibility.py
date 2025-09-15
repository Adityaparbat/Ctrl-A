import os
import io
import re
import json
import tempfile
from typing import Dict, Any, Optional, Tuple

import requests
import urllib.parse

try:
    import trafilatura  # Robust article text extraction
except Exception:
    trafilatura = None  # type: ignore

try:
    from PIL import Image
except Exception:
    Image = None  # type: ignore

try:
    import pytesseract  # OCR
except Exception:
    pytesseract = None  # type: ignore

try:
    from googletrans import Translator  # Simple translation
except Exception:
    Translator = None  # type: ignore

from config import TTS_LANGUAGE, SUPPORTED_LANGUAGES, LANGUAGE_PATTERNS
from notifier import get_disability_type
from tts import speak, synthesize_to_file
import os as _os
PROJECT_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))

# Import GPT processing capabilities
try:
    import sys
    sys.path.append(_os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", "..")))
    from gpt import process_input as gpt_process_input, ask_ai
except Exception:
    gpt_process_input = None
    ask_ai = None


def _safe_text(s: Optional[str]) -> str:
    return (s or "").strip()


def detect_preferred_language(explicit_lang: Optional[str] = None) -> str:
    if explicit_lang and explicit_lang.strip():
        return explicit_lang.strip().lower()
    env_lang = os.getenv("PREFERRED_LANGUAGE", "").strip().lower()
    if env_lang:
        return env_lang
    return TTS_LANGUAGE


def detect_language_from_input(text: str) -> str:
    """Detect user's preferred language from their input text."""
    if not text:
        return TTS_LANGUAGE
    
    text_lower = text.lower()
    
    # Check for explicit language indicators first
    for lang_code, patterns in LANGUAGE_PATTERNS.items():
        if any(pattern in text_lower for pattern in patterns):
            return lang_code
    
    # Check for English words even in Devanagari script
    english_words_in_devanagari = [
        "set", "एन", "अलार्म", "फॉर", "टेकिंग", "मेडिसिन", "एट", "time", "date",
        "remind", "call", "message", "email", "app", "phone", "computer", "internet",
        "google", "facebook", "whatsapp", "youtube", "website", "online", "offline"
    ]
    
    # If text contains English words (even in Devanagari script), treat as English
    if any(word in text_lower for word in english_words_in_devanagari):
        return "en"
    
    # Check for pure English words (Latin script)
    english_indicators = [
        "the", "and", "for", "with", "from", "this", "that", "will", "can", "should",
        "please", "thank", "hello", "hi", "good", "bad", "yes", "no", "ok", "okay",
        "set", "alarm", "reminder", "time", "date", "today", "tomorrow", "yesterday",
        "morning", "afternoon", "evening", "night", "week", "month", "year"
    ]
    
    # Count English words in the text
    english_word_count = sum(1 for word in english_indicators if word in text_lower)
    
    # If significant English words are present, treat as English
    if english_word_count >= 2:
        return "en"
    
    # Check for script detection (basic)
    if any('\u0900' <= char <= '\u097F' for char in text):  # Devanagari script
        # Check for Marathi-specific characters or words
        marathi_indicators = ["महाराष्ट्र", "पुणे", "मुंबई", "मराठी", "आहे", "आणि", "किंवा", "मला", "तुम्ही"]
        hindi_indicators = ["हिंदी", "भारत", "दिल्ली", "मुंबई", "है", "और", "या", "मुझे", "आप"]
        
        marathi_count = sum(1 for indicator in marathi_indicators if indicator in text_lower)
        hindi_count = sum(1 for indicator in hindi_indicators if indicator in text_lower)
        
        if marathi_count > hindi_count:
            return "mr"
        else:
            return "hi"  # Default to Hindi for Devanagari
    
    return "en"  # Default to English


def convert_devanagari_english_to_latin(text: str) -> str:
    """Convert English words written in Devanagari script to Latin script."""
    if not text:
        return text
    
    # Mapping of common English words in Devanagari to Latin
    devanagari_to_latin = {
        "सेट": "set",
        "सट": "set",  # Alternative spelling
        "एन": "an", 
        "अलार्म": "alarm",
        "अलरम": "alarm",  # Alternative spelling
        "फॉर": "for",
        "फर": "for",  # Alternative spelling
        "टेकिंग": "taking",
        "टकग": "taking",  # Alternative spelling
        "मेडिसिन": "medicine",
        "मडसन": "medicine",  # Alternative spelling
        "एट": "at",
        "टाइम": "time",
        "डेट": "date",
        "रिमाइंडर": "reminder",
        "कॉल": "call",
        "मैसेज": "message",
        "ईमेल": "email",
        "ऐप": "app",
        "फोन": "phone",
        "कंप्यूटर": "computer",
        "इंटरनेट": "internet",
        "गूगल": "google",
        "फेसबुक": "facebook",
        "व्हाट्सऐप": "whatsapp",
        "यूट्यूब": "youtube",
        "वेबसाइट": "website",
        "ऑनलाइन": "online",
        "ऑफलाइन": "offline",
        "प्लीज": "please",
        "थैंक": "thank",
        "हेलो": "hello",
        "हाय": "hi",
        "गुड": "good",
        "बैड": "bad",
        "यस": "yes",
        "नो": "no",
        "ओके": "ok",
        "टुडे": "today",
        "टुमॉरो": "tomorrow",
        "यस्टरडे": "yesterday",
        "मॉर्निंग": "morning",
        "आफ्टरनून": "afternoon",
        "ईवनिंग": "evening",
        "नाइट": "night",
        "वीक": "week",
        "मंथ": "month",
        "इयर": "year"
    }
    
    converted_text = text
    for devanagari, latin in devanagari_to_latin.items():
        converted_text = converted_text.replace(devanagari, latin)
        converted_text = converted_text.replace(devanagari.lower(), latin)
    
    return converted_text


def fetch_url_text(url: str) -> str:
    url = _safe_text(url)
    if not url:
        return ""
    try:
        # Trafilatura handles boilerplate removal
        if trafilatura is not None:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                extracted = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
                if extracted:
                    return extracted
        # Fallback: raw HTML->text naive
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
        text = resp.text
        text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
    except Exception:
        return ""


def ocr_image_from_path(image_path: str, target_lang: str = "eng") -> str:
    """Extract text from image using OCR with language support."""
    if not image_path:
        return ""
    try:
        if Image is None or pytesseract is None:
            return ""
        
        image = Image.open(image_path)
        
        # Map language codes to Tesseract language codes
        lang_map = {
            "hi": "hin",  # Hindi
            "mr": "mar",  # Marathi  
            "gu": "guj",  # Gujarati
            "en": "eng",  # English
        }
        
        tesseract_lang = lang_map.get(target_lang, "eng")
        
        # Try with specific language first
        try:
            text = pytesseract.image_to_string(image, lang=tesseract_lang)
            if text.strip():
                return _safe_text(text)
        except Exception:
            pass
        
        # Fallback to English if specific language fails
        text = pytesseract.image_to_string(image, lang="eng")
        return _safe_text(text)
        
    except Exception as e:
        print(f"[OCR] Error processing image: {e}")
        return ""


def summarize_text(text: str, max_sentences: int = 5) -> str:
    text = _safe_text(text)
    if not text:
        return ""
    # Fallback: naive sentence selection
    sentences = re.split(r"(?<=[.!?])\s+", text)
    kept = []
    for s in sentences:
        s_clean = s.strip()
        if not s_clean:
            continue
        kept.append(s_clean)
        if len(kept) >= max_sentences:
            break
    return " ".join(kept)


def _google_news_hl_for(lang: str) -> str:
    l = (lang or "en").lower()
    if l.startswith("hi"):
        return "hi-IN"
    if l.startswith("mr"):
        return "mr-IN"
    if l.startswith("gu"):
        return "gu-IN"
    if l.startswith("en"):
        return "en-IN"
    return "en-IN"


def fetch_news(query: str, lang: str, max_items: int = 6) -> str:
    try:
        import feedparser  # type: ignore
    except Exception:
        return f"Top news about {query}: (RSS client missing)"

    q = urllib.parse.quote(query)
    hl = _google_news_hl_for(lang)
    url = f"https://news.google.com/rss/search?q={q}&hl={hl}&gl=IN&ceid=IN:{hl.split('-')[0]}"
    try:
        feed = feedparser.parse(url)
    except Exception:
        feed = None
    if not feed or not getattr(feed, 'entries', None):
        return f"No news found for {query}."

    lines = []
    for entry in feed.entries[:max_items]:  # type: ignore[attr-defined]
        title = _safe_text(getattr(entry, 'title', ''))
        source = ""
        if hasattr(entry, 'source') and getattr(entry, 'source'):
            try:
                source = _safe_text(getattr(entry.source, 'title', ''))  # type: ignore[attr-defined]
            except Exception:
                source = ""
        if source:
            lines.append(f"- {title} ({source})")
        else:
            lines.append(f"- {title}")
    if not lines:
        return f"No news found for {query}."
    return "\n".join(lines)


def translate_text(text: str, target_lang: str) -> str:
    text = _safe_text(text)
    if not text:
        return ""
    lang = (target_lang or TTS_LANGUAGE).strip().lower()
    # Use googletrans if available
    if Translator is not None:
        try:
            translator = Translator()
            result = translator.translate(text, dest=lang)
            return _safe_text(result.text)
        except Exception:
            pass
    # Last resort: return original text
    return text


def generate_intelligent_response(user_input: str, target_lang: str) -> str:
    """Generate intelligent responses using pattern matching when AI is not available."""
    input_lower = user_input.lower().strip()
    lang = target_lang.lower() if target_lang else "en"
    
    # Get disability type for adaptation
    disability_type = get_disability_type()
    
    # Common question patterns and responses
    responses = {
        # Capital questions
        "capital": {
            "india": {
                "hi": "भारत की राजधानी नई दिल्ली है।",
                "mr": "भारताची राजधानी नवी दिल्ली आहे।",
                "en": "The capital of India is New Delhi."
            },
            "महाराष्ट्र": {
                "hi": "महाराष्ट्र की राजधानी मुंबई है।",
                "mr": "महाराष्ट्राची राजधानी मुंबई आहे।",
                "en": "The capital of Maharashtra is Mumbai."
            },
            "maharashtra": {
                "hi": "महाराष्ट्र की राजधानी मुंबई है।",
                "mr": "महाराष्ट्राची राजधानी मुंबई आहे।",
                "en": "The capital of Maharashtra is Mumbai."
            },
        },
        # Weather questions
        "weather": {
            "hi": "मैं मौसम की जानकारी नहीं दे सकता क्योंकि मैं ऑनलाइन नहीं हूं। आप मौसम ऐप या वेबसाइट का उपयोग करें।",
            "mr": "मी हवामानाची माहिती देऊ शकत नाही कारण मी ऑनलाइन नाही। कृपया हवामान ऍप किंवा वेबसाइट वापरा।",
            "en": "I cannot provide weather information as I'm offline. Please use a weather app or website."
        },
        # Time questions
        "time": {
            "hi": "मैं वर्तमान समय नहीं बता सकता। आप अपने डिवाइस पर समय देखें।",
            "mr": "मी सध्याची वेळ सांगू शकत नाही। कृपया आपल्या डिव्हाइसवर वेळ बघा।",
            "en": "I cannot tell the current time. Please check the time on your device."
        },
        # Greetings
        "hello": {
            "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?",
            "mr": "नमस्कार! मी तुमची कशी मदत करू शकतो?",
            "en": "Hello! How can I help you?"
        },
        "hi": {
            "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?",
            "mr": "नमस्कार! मी तुमची कशी मदत करू शकतो?",
            "en": "Hi! How can I help you?"
        },
        "namaste": {
            "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?",
            "mr": "नमस्कार! मी तुमची कशी मदत करू शकतो?",
            "en": "Namaste! How can I help you?"
        },
    }
    
    # Helper function to get response in appropriate language and format
    def get_response(key, category="general"):
        if category in responses and key in responses[category]:
            if isinstance(responses[category][key], dict):
                response = responses[category][key].get(lang, responses[category][key].get("en", ""))
            else:
                response = responses[category][key]
        else:
            # Default responses
            defaults = {
                "hi": "मुझे इसकी जानकारी नहीं है।",
                "mr": "मला याची माहिती नाही।",
                "en": "I don't have information about this."
            }
            response = defaults.get(lang, defaults["en"])
        
        # Adapt response based on disability type
        return adapt_response_for_disability(response, disability_type)
    
    # Check for capital questions
    if any(word in input_lower for word in ["capital", "राजधानी", "राजधानी क्या", "राजधानी काय"]):
        for key in responses["capital"].keys():
            if key in input_lower:
                return get_response(key, "capital")
        return get_response("unknown", "capital")
    
    # Check for weather questions
    if any(word in input_lower for word in ["weather", "मौसम", "बारिश", "तापमान", "हवामान", "पाऊस"]):
        return get_response("weather", "weather")
    
    # Check for time questions
    if any(word in input_lower for word in ["time", "समय", "कितना बजे", "बजे", "वेळ", "किती वाजले"]):
        return get_response("time", "time")
    
    # Check for greetings
    for greeting in ["hello", "hi", "namaste", "नमस्ते", "नमस्कार"]:
        if greeting in input_lower:
            return get_response(greeting, "hello")
    
    # Check for news keywords
    news_keywords = ["news", "खबर", "समाचार", "बातम्या", "न्यूज", "बातमी", "वृत्त"]
    if any(k in input_lower for k in news_keywords):
        return fetch_news(user_input, target_lang)
    
    # Default response
    defaults = {
        "hi": "मैं आपकी बात समझ गया हूं, लेकिन मैं इस समय ऑनलाइन नहीं हूं। आप कुछ और पूछ सकते हैं।",
        "mr": "मी तुमची बोलणी समजलो आहे, पण मी सध्या ऑनलाइन नाही। तुम्ही काहीतरी वेगळे विचारू शकता।",
        "en": "I understand what you said, but I'm currently offline. You can ask me something else."
    }
    default_response = defaults.get(lang, defaults["en"])
    return adapt_response_for_disability(default_response, disability_type)


def adapt_response_for_disability(text: str, disability_type: str) -> str:
    """Adapt response based on disability type."""
    if not text:
        return text
    
    if disability_type == "visual":
        # For visual disabilities: provide audio-friendly format, shorter sentences
        return adapt_for_visual(text)
    elif disability_type == "hearing":
        # For hearing disabilities: text only, clear formatting
        return adapt_for_hearing(text)
    elif disability_type == "cognitive":
        # For cognitive disabilities: simplified, step-by-step format
        return adapt_for_cognitive(text)
    elif disability_type == "motor":
        # For motor disabilities: easy to navigate format
        return adapt_for_motor(text)
    else:
        # Default: standard format
        return text


def adapt_for_visual(text: str) -> str:
    """Adapt text for users with visual disabilities - audio-friendly format."""
    text = _safe_text(text)
    if not text:
        return ""
    
    # Break into shorter sentences for better audio processing
    sentences = re.split(r"(?<=[.!?])\s+", text)
    adapted_sentences = []
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Keep sentences shorter for better audio comprehension
        if len(sentence) > 100:
            # Split long sentences
            parts = re.split(r'[,;]', sentence)
            adapted_sentences.extend([p.strip() for p in parts if p.strip()])
        else:
            adapted_sentences.append(sentence)
    
    return ". ".join(adapted_sentences) + "."


def adapt_for_hearing(text: str) -> str:
    """Adapt text for users with hearing disabilities - clear visual format."""
    text = _safe_text(text)
    if not text:
        return ""
    
    # Add clear formatting and structure for visual reading
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Add visual indicators for important information
        if any(keyword in line.lower() for keyword in ["important", "महत्वपूर्ण", "महत्वाचे", "warning", "चेतावनी"]):
            formatted_lines.append(f"⚠️ {line}")
        elif line.endswith('?'):
            formatted_lines.append(f"❓ {line}")
        elif line.endswith('!'):
            formatted_lines.append(f"❗ {line}")
        else:
            formatted_lines.append(f"📝 {line}")
    
    return "\n".join(formatted_lines)


def adapt_for_cognitive(text: str) -> str:
    """Adapt text for users with cognitive disabilities - simplified format."""
    text = _safe_text(text)
    if not text:
        return ""
    
    # Break into bullet-like short lines
    sentences = re.split(r"(?<=[.!?])\s+", text)
    simple_lines = []
    
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        
        # Keep lines short and simple
        if len(s) > 140:
            # Split by comma as a rough heuristic
            parts = [p.strip() for p in s.split(",") if p.strip()]
            simple_lines.extend(parts)
        else:
            simple_lines.append(s)
    
    # Limit number of steps to avoid overload
    simple_lines = simple_lines[:12]
    return "\n".join(f"• {line}" for line in simple_lines)


def adapt_for_motor(text: str) -> str:
    """Adapt text for users with motor disabilities - easy navigation format."""
    text = _safe_text(text)
    if not text:
        return ""
    
    # Format for easy navigation with assistive technologies
    lines = text.split('\n')
    formatted_lines = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        
        # Add numbering for easy navigation
        formatted_lines.append(f"{i}. {line}")
    
    return "\n".join(formatted_lines)


def generate_output(summary_text: str, target_lang: str) -> Tuple[str, Optional[str]]:
    """Return (final_text, audio_path_if_any) based on disability type and language.

    - visual: produce audio file, minimal text
    - hearing: text only, no audio
    - cognitive: simplified step list, and audio too for redundancy
    - others: text + audio
    """
    dtype = get_disability_type()
    lang = detect_preferred_language(target_lang)

    final_text = summary_text
    if dtype == "cognitive":
        final_text = adapt_for_cognitive(summary_text)

    audio_path: Optional[str] = None
    if dtype == "hearing":
        # Text only
        return final_text, None

    try:
        # Synthesize to a temp file, do not auto-play
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "accessible_reply.mp3")
            synthesize_to_file(final_text, lang=lang, out_path=out_file)
            # Persist by copying to project root for user convenience
            dest = os.path.abspath(os.path.join(PROJECT_ROOT, "reply.mp3"))
            try:
                import shutil
                shutil.copyfile(out_file, dest)
                audio_path = dest
            except Exception:
                audio_path = out_file
    except Exception:
        audio_path = None

    return final_text, audio_path


def process_accessible(
    input_type: str,
    payload: str,
    preferred_language: Optional[str] = None,
) -> Dict[str, Any]:
    """Unified entry for Accessibility Assistant.

    input_type: "voice" (already transcribed), "url", "image", or "query" (text)
    payload: content depending on type (text or path or URL)
    preferred_language: language code like "hi", "mr", "gu", "en"
    """
    input_type_l = (input_type or "query").strip().lower()
    
    # Auto-detect language from input if not explicitly provided
    if not preferred_language and input_type_l in ("voice", "query", "text"):
        detected_lang = detect_language_from_input(payload)
        target_lang = detected_lang
    else:
        target_lang = detect_preferred_language(preferred_language)

    raw_text = ""
    if input_type_l == "url":
        raw_text = fetch_url_text(payload)
    elif input_type_l == "image":
        raw_text = ocr_image_from_path(payload, target_lang)
    elif input_type_l in ("voice", "query", "text"):
        pl = _safe_text(payload)
        if pl.startswith("http://") or pl.startswith("https://"):
            raw_text = fetch_url_text(pl)
        else:
            # Convert Devanagari English words to Latin script for better AI processing
            if target_lang == "en":
                pl_converted = convert_devanagari_english_to_latin(pl)
                if pl_converted != pl:
                    print(f"[Accessibility] Converted input: '{pl}' -> '{pl_converted}'")
                    pl = pl_converted
            
            # Use AI processing for intelligent understanding
            if gpt_process_input is not None:
                try:
                    gpt_result = gpt_process_input(input_type_l, pl)
                    if gpt_result and gpt_result.get("assistant_reply") and not gpt_result["assistant_reply"].startswith("I'm currently offline"):
                        raw_text = gpt_result["assistant_reply"]
                    else:
                        # AI is offline, use intelligent fallback responses
                        raw_text = generate_intelligent_response(pl, target_lang)
                except Exception as e:
                    # Fallback to intelligent responses if AI processing fails
                    print(f"[Accessibility] AI processing failed: {e}")
                    raw_text = generate_intelligent_response(pl, target_lang)
            else:
                # Fallback when GPT is not available
                raw_text = generate_intelligent_response(pl, target_lang)
    else:
        raw_text = _safe_text(payload)

    if not raw_text:
        return {
            "ok": False,
            "error": "No content extracted",
        }

    # If we got an AI response, it's already processed - use it directly
    # Only do additional processing for non-AI content
    if gpt_process_input is not None and input_type_l in ("voice", "query", "text") and not any(raw_text.startswith(prefix) for prefix in ["http://", "https://"]):
        # This is likely an AI-generated response, use it as-is
        final_text, audio_path = generate_output(raw_text, target_lang)
    else:
        # Original processing for URLs, images, and non-AI content
        summary = summarize_text(raw_text)
        translated = translate_text(summary, target_lang)
        final_text, audio_path = generate_output(translated, target_lang)

    return {
        "ok": True,
        "language": target_lang,
        "text": final_text,
        "audio_file": audio_path,
    }


