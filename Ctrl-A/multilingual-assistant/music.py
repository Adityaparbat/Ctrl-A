try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None
import os
import shlex
from typing import Optional
from nlu import parse_command
import datetime
import threading
import time
import urllib.request
import json
import re
from twilio.rest import Client
import os

# ---- Twilio WhatsApp Notification Utility ----
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC1c20e05fa11039eb844c03384b6f8001")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "955b2358aeb5f66d9a3a49022121550a")
TWILIO_WA_FROM = os.getenv("TWILIO_WA_FROM", "whatsapp:+12566995032")  # Twilio sandbox WhatsApp number
TWILIO_WA_TO = os.getenv("TWILIO_WA_TO", "whatsapp:+917796106770")    # Your WhatsApp number joined to sandbox

def send_sms_notification(body: str, to_number: str):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        message = client.messages.create(
            body=body,
            from_=TWILIO_SMS_FROM,
            to=to_number,
        )
        print(f"SMS sent: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")
# ------------------------------
# Function to play music from YouTube
# ------------------------------
def play_music(query):
    if YoutubeDL is None:
        print("[ERROR] yt-dlp is not installed. Install it with: py -m pip install yt-dlp")
        return
    print(f"[INFO] Searching YouTube for: {query}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        # Force a single top result for plain-text queries
        'default_search': 'ytsearch1',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Accept plain text like "play relaxing music" or a song name
            info = ydl.extract_info(query, download=True)
            print("[SUCCESS] Music downloaded and ready to play.")

            # Get the final, post-processed output filename
            filename = None
            try:
                if 'requested_downloads' in info and info['requested_downloads']:
                    rd = info['requested_downloads'][0]
                    filename = rd.get('filepath') or rd.get('filename')
            except Exception:
                pass

            # Fallbacks if requested_downloads not available
            if not filename:
                base_info = info['entries'][0] if ('entries' in info and info['entries']) else info
                candidate = ydl.prepare_filename(base_info)
                # After FFmpegExtractAudio, extension becomes mp3
                root, _ = os.path.splitext(candidate)
                filename = root + '.mp3'

            # Play audio using default system player
            try:
                # Best on Windows
                os.startfile(filename)
            except AttributeError:
                # Fallback for non-Windows
                quoted = shlex.quote(filename)
                if os.name == 'posix':
                    os.system(f'xdg-open {quoted}')
                else:
                    os.system(f'start "" {quoted}')
        except Exception as e:
            print("[ERROR] Failed to play music:", e)

# ------------------------------
# Main handler function
# ------------------------------
def _extract_song_query(user_input: str) -> Optional[str]:
    intent, entities, confidence = parse_command(user_input)
    # Only play when the intent is confidently play_music
    if intent == "play_music" and confidence >= 0.5:
        if entities:
            return entities[0]
        # Heuristic: take words after 'play'
        lower = user_input.lower()
        if "play" in lower:
            idx = lower.find("play")
            phrase = user_input[idx + len("play"):].strip()
            if phrase:
                return phrase
        return user_input
    # For non-music intents, do nothing
    return None


import urllib.request
import json
from typing import Optional

def _fetch_weather_text(location: Optional[str]) -> str:
    try:
        loc = (location or "").strip()
        if not loc:
            url = "https://wttr.in/?format=j1"
        else:
            loc_path = loc.replace(" ", "+")
            url = f"https://wttr.in/{loc_path}?format=j1"
        
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        current = data.get("current_condition", [{}])[0]
        temp_c = current.get("temp_C", "N/A")
        feels_c = current.get("FeelsLikeC", "N/A")
        descs = current.get("weatherDesc", [{"value": "No description"}])
        desc = descs[0].get("value", "No description")
        
        # Use the user-provided location in output, fallback only if missing
        where = location or "your area"
        return f"Weather in {where}: {desc}, {temp_c}°C (feels like {feels_c}°C)."
    
    except Exception:
        # Never return an exception; provide fallback message
        return f"Weather information for '{location or 'your location'}' is currently unavailable. Please try again later."


_reminders = []  # list of tuples (time_epoch, message)

# Optional Windows toast notifications
try:
    from win10toast import ToastNotifier  # type: ignore
    _toaster = ToastNotifier()
except Exception:
    _toaster = None


def _extract_message_from_text(user_input: str) -> Optional[str]:
    lower = user_input.lower()
    if " for " in lower:
        idx = lower.find(" for ")
        msg = user_input[idx + len(" for "):].strip()
        return msg or None
    return None


def _parse_time_from_text(user_input: str) -> Optional[datetime.datetime]:
    now = datetime.datetime.now()
    text = user_input.lower().strip()

    # in X minutes/hours
    m = re.search(r"\bin\s+(\d+)\s*(minute|minutes|min|hour|hours|hr|hrs)\b", text)
    if m:
        amount = int(m.group(1))
        unit = m.group(2)
        if unit.startswith("hour") or unit in ("hr", "hrs"):
            return now + datetime.timedelta(hours=amount)
        return now + datetime.timedelta(minutes=amount)

    # at HH[:|.]MM [am|pm], or at H [am|pm]
    m = re.search(r"\bat\s+(\d{1,2})(?::|(\.)(\d{2}))?\s*(am|pm)?\b", text)
    if m:
        hour = int(m.group(1))
        minute = 0
        if m.group(3):
            minute = int(m.group(3))
        ampm = m.group(4)
        if ampm == "pm" and hour != 12:
            hour += 12
        if ampm == "am" and hour == 12:
            hour = 0
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target < now:
            target = target + datetime.timedelta(days=1)
        return target

    # at HH:MM 24h (redundant but explicit)
    m = re.search(r"\bat\s+(\d{1,2}):(\d{2})\b", text)
    if m:
        hour = int(m.group(1))
        minute = int(m.group(2))
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target < now:
            target = target + datetime.timedelta(days=1)
        return target
    return None


def _schedule_reminder(target_time: datetime.datetime, message: str, recipient_number: str) -> str:
    epoch = int(target_time.timestamp())
    _reminders.append((epoch, message or "Reminder", recipient_number))

    def worker():
        while True:
            time.sleep(1)
            now_epoch = int(time.time())
            due = [(t, m, num) for (t, m, num) in list(_reminders) if t <= now_epoch]
            for t, m, num in due:
                if _toaster is not None:
                    try:
                        _toaster.show_toast("Reminder", m, duration=10, threaded=True)
                    except Exception:
                        pass
                print(f"[REMINDER] {m}")
                try:
                    # Send SMS notification on reminder trigger
                    send_sms_notification(f"🔔 Reminder: {m}", num)
                except Exception as e:
                    print(f"Failed to send SMS: {e}")
                try:
                    _reminders.remove((t, m, num))
                except ValueError:
                    pass
            if not _reminders:
                break

    threading.Thread(target=worker, daemon=True).start()
    return f"Reminder set for {target_time.strftime('%Y-%m-%d %H:%M')} with message: {message or 'Reminder'}"

def handle_user_command(user_input):
    intent, entities, confidence = parse_command(user_input)
    if intent == "play_music" and confidence >= 0.5:
        query = _extract_song_query(user_input)
        if not query:
            print("[INFO] Nothing to play.")
            return
        play_music(query)
        return

    if intent == "get_weather" and confidence >= 0.5:
        # Extract location from entities or parse from user input
        location = None
        if entities:
            location = entities[0]
        else:
            # Fallback: look for common location patterns in the input
            import re
            # Look for "in [location]" or "for [location]" patterns
            patterns = [
                r"in\s+([a-zA-Z\s]+?)(?:\s|$)",
                r"for\s+([a-zA-Z\s]+?)(?:\s|$)",
                r"at\s+([a-zA-Z\s]+?)(?:\s|$)"
            ]
            for pattern in patterns:
                match = re.search(pattern, user_input.lower())
                if match:
                    location = match.group(1).strip()
                    break
        
        print(_fetch_weather_text(location))
        return

    if intent == "set_alarm" and confidence >= 0.5:
        target_time = _parse_time_from_text(user_input)
        if not target_time:
            target_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
        message = _extract_message_from_text(user_input) or (" ".join(entities) if entities else None) or "Reminder"
        print(_schedule_reminder(target_time, message, recipient_number))
        return

    print("[INFO] Intent not supported for automation yet.")

# ------------------------------
# Program entry point
# ------------------------------
if __name__ == "__main__":
    user_input = input("What do you want to play?\n")  # e.g., "Play relaxing music"
    recipient_number = input("Enter your mobile number in +91xxxxxxxxxx format to receive SMS reminders:\n")
    handle_user_command(user_input)
