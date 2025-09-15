import os
import sys
from typing import Literal

from tts import speak


DisabilityType = Literal["hearing", "visual", "cognitive", "motor", "none"]


def get_disability_type() -> DisabilityType:
    value = (os.getenv("DISABILITY_TYPE", "none").strip().lower())
    if value in ("hearing", "visual", "cognitive", "motor", "none"):
        return value  # type: ignore[return-value]
    return "none"  # type: ignore[return-value]


def notify(message: str) -> None:
    dtype = get_disability_type()

    if dtype == "hearing":
        # Visual emphasis for Deaf/HoH users: large console banner
        banner = f"\n{'='*60}\nREMINDER: {message}\n{'='*60}\n"
        print(banner)
        return

    if dtype == "visual":
        # Audio-first for blind/low-vision users
        speak(message)
        return

    if dtype == "cognitive":
        # Short, simple, redundant cue
        speak(message)
        print(f"REMINDER: {message}")
        return

    if dtype == "motor":
        # Avoid complex interactions; simple print + audio
        speak(message)
        print(f"REMINDER: {message}")
        return

    # Default: both print and speak
    speak(message)
    print(f"REMINDER: {message}")


