try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None
import os
import shlex
from typing import Optional
from nlu import parse_command

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


def handle_user_command(user_input):
    query = _extract_song_query(user_input)
    if not query:
        print("[INFO] Intent not play_music. No action taken.")
        return
    play_music(query)

# ------------------------------
# Program entry point
# ------------------------------
if __name__ == "__main__":
    user_input = input("What do you want to play?\n")  # e.g., "Play relaxing music"
    handle_user_command(user_input)
