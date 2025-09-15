# config.py

# Default language (can change to "en", "hi", "mr", etc.)
STT_LANGUAGE = "hi-IN"   # Speech-to-text language
TTS_LANGUAGE = "hi"      # Text-to-speech language

# Supported languages for the assistant
SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi", 
    "mr": "Marathi",
    "gu": "Gujarati"
}

# Language detection patterns
LANGUAGE_PATTERNS = {
    "hi": ["हिंदी", "hindi", "हिंदी में", "in hindi"],
    "mr": ["मराठी", "marathi", "मराठी में", "in marathi", "महाराष्ट्र"],
    "gu": ["ગુજરાતી", "gujarati", "ગુજરાતી માં", "in gujarati"],
    "en": ["english", "in english", "अंग्रेजी", "अंग्रेजी में"]
}