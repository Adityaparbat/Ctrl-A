#!/usr/bin/env python3
"""
Voice Music Player - Integrated STT + Music
Combines stt.py and music.py for voice-controlled music playback
"""

import tempfile
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from config import STT_LANGUAGE
from music import handle_user_command
from nlu import parse_command

recognizer = sr.Recognizer()

def autocorrect_text(text):
    """Autocorrect common transcription errors"""
    corrections = {
        # Common music command corrections
        'plee': 'play',
        'plea': 'play',
        'pray': 'play',
        'plae': 'play',
        'ple': 'play',
        'paly': 'play',
        'palay': 'play',
        
        # Song name corrections
        'paru': 'paro',
        'paroo': 'paro',
        'parow': 'paro',
        
        # Other common words
        'musik': 'music',
        'musick': 'music',
        'songs': 'song',
        'sing': 'song',
        'sang': 'song',
        
        # Intent corrections
        'sit': 'set',
        'sat': 'set',
        'remainder': 'reminder',
        'remind': 'reminder',
        'allarm': 'alarm',
        'alam': 'alarm'
    }
    
    corrected_text = text.lower()
    words = corrected_text.split(' ')
    corrected_words = [corrections.get(word.replace('.,!?;:', ''), word) for word in words]
    
    return ' '.join(corrected_words)

def listen_and_process(duration_seconds: int = 5, sample_rate: int = 16000):
    """Record audio, transcribe, autocorrect, and process command"""
    print(f"🎤 Speak in {STT_LANGUAGE} ...")
    try:
        # Record audio
        recording = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav_path = tmp.name
        sf.write(wav_path, recording, sample_rate)

        # Transcribe audio
        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio, language=STT_LANGUAGE)
        
        if not text:
            print("⚠ No speech detected")
            return
            
        # Autocorrect the text
        corrected_text = autocorrect_text(text)
        print(f"🗣 You said: {corrected_text}")
        
        # Check intent
        intent, entities, confidence = parse_command(corrected_text)
        print(f"🎯 Intent: {intent} (confidence: {confidence:.2f})")
        
        if intent == "play_music" and confidence >= 0.5:
            print("🎵 Playing music...")
            handle_user_command(corrected_text)
        else:
            print(f"❌ Not a music command: {intent}")
            
    except sr.UnknownValueError:
        print("⚠ Could not understand audio")
    except sr.RequestError as e:
        print("⚠ Speech recognition error:", e)
    except Exception as e:
        print("⚠ Error:", e)

def main():
    """Main loop for voice music player"""
    print("🎵 Voice Music Player")
    print("=" * 50)
    print("Commands:")
    print("- Say 'play [song name]' to play music")
    print("- Say 'set reminder' for non-music commands")
    print("- Press Ctrl+C to exit")
    print("=" * 50)
    
    try:
        while True:
            input("\nPress Enter to start listening...")
            listen_and_process()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
