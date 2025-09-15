from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session, Response, send_file, send_from_directory
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from database import db
import os
import re
from datetime import datetime
import threading
import requests
import shutil
import subprocess
import tempfile
import uuid

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Email validation regex
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_REGEX = re.compile(r'^\+?1?\d{9,15}$')

# FFmpeg binary resolution (allows overriding via env var)
FFMPEG_BIN = os.getenv('FFMPEG_BIN') or shutil.which('ffmpeg')

# Directory to store temporary media files
MEDIA_DIR = os.path.join(tempfile.gettempdir(), 'ctrl_a_media')
os.makedirs(MEDIA_DIR, exist_ok=True)

# Common headers for upstream media CDNs
_DEFAULT_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)
_COMMON_UPSTREAM_HEADERS = {
    'User-Agent': _DEFAULT_UA,
    'Accept': '*/*',
    'Accept-Encoding': 'identity;q=1, *;q=0',
    'Connection': 'keep-alive',
    'Referer': 'https://www.youtube.com/',
}

# Paths
BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..'))
OFFLINE_DIR = os.path.abspath(os.path.join(ROOT_DIR, 'offline_chatbot'))

def validate_email(email):
    """Validate email format"""
    return EMAIL_REGEX.match(email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    return PHONE_REGEX.match(phone) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

@app.route('/')
def index():
    """Redirect to landing page"""
    return redirect('/landing')

@app.route('/landing')
def landing():
    """Serve landing page"""
    with open('landing.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/login')
def login_page():
    """Serve login page"""
    with open('login.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/signup')
def signup_page():
    """Serve signup page"""
    with open('signup.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/dashboard')
def dashboard():
    """Serve dashboard page"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        return redirect('/login')
    
    # Validate session
    session_data = db.validate_session(session_token)
    if not session_data['success']:
        session.clear()
        return redirect('/login')
    
    with open('dashboard.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/welfare_schemes')
def welfare_schemes():
    """Serve welfare schemes page"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        return redirect('/login')
    
    # Validate session
    session_data = db.validate_session(session_token)
    if not session_data['success']:
        session.clear()
        return redirect('/login')
    
    with open('welfare_schemes.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/ai_assistant')
def ai_assistant():
    """Serve AI assistant page"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        return redirect('/login')
    
    # Validate session
    session_data = db.validate_session(session_token)
    if not session_data['success']:
        session.clear()
        return redirect('/login')
    
    with open('ai_assistant.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/legal_rights')
def legal_rights():
    """Serve legal rights page"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        return redirect('/login')
    
    # Validate session
    session_data = db.validate_session(session_token)
    if not session_data['success']:
        session.clear()
        return redirect('/login')
    
    with open('legal_rights.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/daily_tasks')
def daily_tasks():
    """Serve daily tasks page"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        return redirect('/login')
    
    # Validate session
    session_data = db.validate_session(session_token)
    if not session_data['success']:
        session.clear()
        return redirect('/login')
    
    with open('daily_tasks.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/camera_navigation')
def camera_navigation():
    """Serve camera navigation page"""
    # Check if user is logged in
    session_token = session.get('session_token')
    if not session_token:
        return redirect('/login')
    
    # Validate session
    session_data = db.validate_session(session_token)
    if not session_data['success']:
        session.clear()
        return redirect('/login')
    
    # Redirect to mounted Half1 UI
    return redirect('/navigation/')

# -------------------------------
# Camera Navigation mount (embed half1/app.py under /navigation)
# -------------------------------
try:
    import sys
    BASE_DIR = os.path.dirname(__file__)
    HALF1_DIR = os.path.join(BASE_DIR, 'half1')
    if HALF1_DIR not in sys.path:
        sys.path.insert(0, HALF1_DIR)

    # Import the existing app as a WSGI app
    from half1.app import app as nav_app  # type: ignore

    # Mount under /navigation
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/navigation': nav_app
    })
    print('[Navigation] Mounted half1.app under /navigation')
except Exception as e:
    print(f'[Navigation] Failed to mount half1.app under /navigation: {e}')

@app.route('/admin_schemes')
def admin_schemes():
    """Serve admin schemes management page"""
    print("Admin schemes route accessed")  # Debug log
    
    # Check if user is admin
    is_admin = session.get('is_admin', False)
    if not is_admin:
        print("User is not admin, redirecting to admin login")  # Debug log
        return redirect('/admin_login')
    
    print("Serving admin_schemes.html")  # Debug log
    try:
        with open('admin_schemes.html', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Admin page loaded successfully, content length: {len(content)}")  # Debug log
            return content
    except FileNotFoundError:
        print("admin_schemes.html file not found")  # Debug log
        return "Admin page not found. Please ensure admin_schemes.html exists in the Ctrl-A directory.", 404
    except Exception as e:
        print(f"Error loading admin page: {e}")  # Debug log
        return f"Error loading admin page: {str(e)}", 500

@app.route('/test_sign_language')
def test_sign_language():
    """Serve sign language test page"""
    with open('test_sign_language.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/admin_test')
def admin_test():
    """Test admin page without authentication"""
    print("Admin test route accessed")  # Debug log
    try:
        with open('admin_schemes.html', 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Admin test page loaded successfully, content length: {len(content)}")  # Debug log
            return content
    except FileNotFoundError:
        print("admin_schemes.html file not found")  # Debug log
        return "Admin page not found. Please ensure admin_schemes.html exists in the Ctrl-A directory.", 404
    except Exception as e:
        print(f"Error loading admin test page: {e}")  # Debug log
        return f"Error loading admin test page: {str(e)}", 500

@app.route('/debug_admin')
def debug_admin():
    """Debug admin access page"""
    with open('debug_admin.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/admin_login')
def admin_login():
    """Serve admin login page"""
    with open('admin_login.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/sign_language.js')
def serve_sign_language_js():
    try:
        with open('sign_language.js', 'r', encoding='utf-8') as f:
            return Response(f.read(), mimetype='application/javascript')
    except Exception as e:
        return f"Unable to load sign_language.js: {str(e)}", 404

@app.route('/api/admin-login', methods=['POST'])
def api_admin_login():
    """API endpoint for admin login"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        # Check admin credentials
        if username == 'admin' and password == 'password':
            # Set admin session
            session['is_admin'] = True
            session['admin_username'] = username
            
            return jsonify({
                'success': True,
                'message': 'Admin login successful',
                'redirect': '/admin_schemes'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid admin credentials'
            }), 401
            
    except Exception as e:
        print(f"Admin login error: {e}")
        return jsonify({
            'success': False,
            'message': 'Login failed. Please try again.'
        }), 500

@app.route('/api/admin-logout', methods=['POST'])
def api_admin_logout():
    """API endpoint for admin logout"""
    try:
        session.pop('is_admin', None)
        session.pop('admin_username', None)
        
        return jsonify({
            'success': True,
            'message': 'Admin logged out successfully',
            'redirect': '/dashboard'
        })
    except Exception as e:
        print(f"Admin logout error: {e}")
        return jsonify({
            'success': False,
            'message': 'Logout failed'
        }), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password are required"})
        
        if not validate_email(email):
            return jsonify({"success": False, "error": "Invalid email format"})
        
        # Authenticate user
        auth_result = db.authenticate_user(email, password)
        if not auth_result['success']:
            return jsonify(auth_result)
        
        # Create session
        session_result = db.create_session(auth_result['user']['id'])
        if not session_result['success']:
            return jsonify(session_result)
        
        # Store session in Flask session
        session['session_token'] = session_result['session_token']
        session['user_id'] = auth_result['user']['id']
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "redirect": "/dashboard"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """API endpoint for user registration"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        disability_type = data.get('disability_type', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        # Validation
        if not all([email, phone, disability_type, password, confirm_password]):
            return jsonify({"success": False, "error": "All fields are required"})
        
        if not validate_email(email):
            return jsonify({"success": False, "error": "Invalid email format"})
        
        if not validate_phone(phone):
            return jsonify({"success": False, "error": "Invalid phone number format"})
        
        if password != confirm_password:
            return jsonify({"success": False, "error": "Passwords do not match"})
        
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg})
        
        # Create user
        result = db.create_user(email, phone, disability_type, password)
        if not result['success']:
            return jsonify(result)
        
        # Auto-login after successful registration
        auth_result = db.authenticate_user(email, password)
        if auth_result['success']:
            session_result = db.create_session(auth_result['user']['id'])
            if session_result['success']:
                session['session_token'] = session_result['session_token']
                session['user_id'] = auth_result['user']['id']
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "redirect": "/dashboard"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """API endpoint for user logout"""
    try:
        session_token = session.get('session_token')
        if session_token:
            db.logout_user(session_token)
        
        session.clear()
        return jsonify({
            "success": True,
            "message": "Logout successful",
            "redirect": "/landing"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/forgot-password', methods=['POST'])
def api_forgot_password():
    """API endpoint for forgot password"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"})
        
        if not validate_email(email):
            return jsonify({"success": False, "error": "Invalid email format"})
        
        # Create password reset token
        result = db.create_password_reset_token(email)
        if not result['success']:
            return jsonify(result)
        
        # In a real application, you would send an email with the reset link
        # For demo purposes, we'll return the token
        reset_link = f"/reset-password?token={result['token']}"
        
        return jsonify({
            "success": True,
            "message": f"Password reset link: {reset_link}",
            "reset_link": reset_link
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/reset-password', methods=['POST'])
def api_reset_password():
    """API endpoint for password reset"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if not all([token, new_password, confirm_password]):
            return jsonify({"success": False, "error": "All fields are required"})
        
        if new_password != confirm_password:
            return jsonify({"success": False, "error": "Passwords do not match"})
        
        is_valid, error_msg = validate_password(new_password)
        if not is_valid:
            return jsonify({"success": False, "error": error_msg})
        
        # Reset password
        result = db.reset_password(token, new_password)
        if not result['success']:
            return jsonify(result)
        
        return jsonify({
            "success": True,
            "message": "Password reset successful",
            "redirect": "/login"
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/user-info')
def api_user_info():
    """API endpoint to get current user info"""
    try:
        session_token = session.get('session_token')
        if not session_token:
            return jsonify({"success": False, "error": "Not logged in"})
        
        session_data = db.validate_session(session_token)
        if not session_data['success']:
            session.clear()
            return jsonify({"success": False, "error": "Invalid session"})
        
        return jsonify({
            "success": True,
            "user": session_data['user']
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tts', methods=['POST'])
def api_tts():
    """API endpoint for text-to-speech"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        language = data.get('language', 'en')
        
        if not text:
            return jsonify({"success": False, "error": "No text provided"})
        
        # Import TTS functionality
        import tempfile
        import os
        from gtts import gTTS
        import base64
        
        # Map UI language codes to gTTS language codes
        lang_map = {
            'en': 'en', 'hi': 'hi', 'es': 'es', 'fr': 'fr', 'de': 'de',
            'ja': 'ja', 'ko': 'ko', 'zh': 'zh-CN', 'mr': 'mr', 'gu': 'gu'
        }
        tts_lang = lang_map.get((language or 'en').lower(), 'en')
        
        # Generate speech
        tts = gTTS(text=text, lang=tts_lang)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            
            # Read file and convert to base64
            with open(tmp_file.name, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            # Convert to base64
            audio_b64 = base64.b64encode(audio_data).decode('utf-8')
            
            return jsonify({
                "success": True,
                "audio_base64": audio_b64,
                "text": text,
                "language": tts_lang
            })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/ai-assistant', methods=['POST'])
def api_ai_assistant():
    """API endpoint for AI assistant"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        language = data.get('language', 'en')
        conversation_history = data.get('conversation_history', []) or []
        
        if not message:
            return jsonify({"success": False, "error": "No message provided"})
        
        # ACTION HANDLERS: lightweight intents that trigger app features
        try:
            import sys as _sys
            import os as _os
            ML_DIR = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), 'multilingual-assistant'))
            if ML_DIR not in _sys.path:
                _sys.path.append(ML_DIR)
            from nlu import parse_command  # type: ignore
            intent, entities, confidence = parse_command(message)
            if intent == 'play_music' and float(confidence or 0) >= 0.5:
                # Build a song query
                query = None
                if entities:
                    query = entities[0]
                if not query:
                    lower = message.lower()
                    if 'play' in lower:
                        idx = lower.find('play')
                        q = message[idx + len('play'):].strip()
                        if q:
                            query = q
                query = query or message
                # Fire and forget playback using existing music module
                try:
                    from music import play_music  # type: ignore
                    threading.Thread(target=play_music, args=(query,), daemon=True).start()
                    resp_text = (
                        f"Playing: {query}. If audio does not start, ensure yt-dlp and ffmpeg are installed. "
                        f"Tip: install with 'pip install yt-dlp' and add ffmpeg to PATH."
                    )
                    return jsonify({
                        "success": True,
                        "response": resp_text,
                        "audio_url": None
                    })
                except Exception as _e:
                    # Continue to normal LLM flow if playback fails
                    pass
        except Exception:
            # NLU not available; continue to LLM/heuristics
            pass
        
        # Build messages for LLM including broad, domain-agnostic system prompt and history
        system_prompt = (
            "You are a highly capable, domain-agnostic assistant like ChatGPT. "
            "Answer any question across any topic with clear, accurate, and concise explanations. "
            "Provide step-by-step guidance when helpful, summarize complex ideas simply, and include brief examples. "
            "Use the user's language when apparent. If unsure, ask a short clarifying question after your best attempt."
        )
        messages = [{"role": "system", "content": system_prompt}]
        for turn in conversation_history:
            role = turn.get('role')
            content = turn.get('content', '')
            if role in ('user', 'assistant') and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})
        
        # Use LLM integration if configured, fallback otherwise
        response_text = None
        try:
            import sys as _sys
            import os as _os
            PROJECT_ROOT = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "..", ".."))
            if PROJECT_ROOT not in _sys.path:
                _sys.path.append(PROJECT_ROOT)
            import gpt  # type: ignore
            response_text = gpt.llm_chat(messages, max_tokens=800)
        except Exception:
            response_text = None
        
        if not response_text:
            # Fallback generic response for any domain
            response_text = generate_generic_response(message)
        
        # Generate audio response (best-effort)
        audio_b64 = None
        try:
            import tempfile
            import os
            from gtts import gTTS
            import base64
            lang_map = {
                'en': 'en', 'hi': 'hi', 'es': 'es', 'fr': 'fr', 'de': 'de',
                'ja': 'ja', 'ko': 'ko', 'zh': 'zh-CN', 'mr': 'mr', 'gu': 'gu'
            }
            tts_lang = lang_map.get((language or 'en').lower(), 'en')
            tts = gTTS(text=response_text, lang=tts_lang)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                with open(tmp_file.name, 'rb') as f:
                    audio_data = f.read()
                os.unlink(tmp_file.name)
                audio_b64 = base64.b64encode(audio_data).decode('utf-8')
        except Exception:
            audio_b64 = None
        
        return jsonify({
            "success": True,
            "response": response_text,
            "audio_url": f"data:audio/mp3;base64,{audio_b64}" if audio_b64 else None
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/stream')
def api_stream():
    """Proxy remote audio to avoid CORS and expose a same-origin URL.

    Supports HTTP Range requests so the browser can seek/buffer audio.
    """
    src = request.args.get('src', '')
    if not src:
        return "Missing src", 400
    try:
        headers = dict(_COMMON_UPSTREAM_HEADERS)
        # Forward Range header for partial content
        if 'Range' in request.headers:
            headers['Range'] = request.headers['Range']
        app.logger.debug(f"[stream] GET {src} headers={headers}")
        upstream = requests.get(src, headers=headers, stream=True, timeout=25)
        status = upstream.status_code  # 200 or 206
        content_type = upstream.headers.get('Content-Type', 'audio/mpeg')
        content_length = upstream.headers.get('Content-Length')
        content_range = upstream.headers.get('Content-Range')
        accept_ranges = upstream.headers.get('Accept-Ranges', 'bytes')

        def generate():
            for chunk in upstream.iter_content(chunk_size=64 * 1024):
                if chunk:
                    yield chunk
        resp = Response(generate(), status=status)
        resp.headers['Content-Type'] = content_type
        resp.headers['Cache-Control'] = 'no-store'
        resp.headers['Accept-Ranges'] = accept_ranges
        if content_length:
            resp.headers['Content-Length'] = content_length
        if content_range:
            resp.headers['Content-Range'] = content_range
        return resp
    except Exception as e:
        app.logger.error(f"[stream] error: {e}")
        return f"Stream error: {e}", 502


@app.route('/api/stream-mp3')
def api_stream_mp3():
    """Transcode/remux remote audio to MP3 for maximum browser compatibility.

    Requires ffmpeg in PATH or FFMPEG_BIN env var. Streams as audio/mpeg.
    """
    src = request.args.get('src', '')
    if not src:
        return "Missing src", 400
    ffmpeg_bin = os.getenv('FFMPEG_BIN') or FFMPEG_BIN
    if not ffmpeg_bin:
        return "ffmpeg not found on PATH (set FFMPEG_BIN)", 500
    try:
        cmd = [
            ffmpeg_bin, '-hide_banner', '-loglevel', 'error',
            '-reconnect', '1', '-reconnect_streamed', '1', '-reconnect_delay_max', '10',
            '-i', src,
            '-vn', '-acodec', 'libmp3lame', '-b:a', '192k', '-f', 'mp3', 'pipe:1'
        ]
        app.logger.debug(f"[stream-mp3] using ffmpeg: {ffmpeg_bin}")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**6)

        def generate():
            try:
                while True:
                    chunk = process.stdout.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
            finally:
                try:
                    process.kill()
                except Exception:
                    pass
        return Response(generate(), headers={
            'Content-Type': 'audio/mpeg',
            'Cache-Control': 'no-store'
        })
    except Exception as e:
        app.logger.error(f"[stream-mp3] error: {e}")
        return f"Stream mp3 error: {e}", 502


@app.route('/api/play-music', methods=['POST'])
def api_play_music():
    """Search YouTube for the query and return a direct audio stream URL.

    Returns JSON: { title, url, duration, watch_url, thumbnail, mp3_url, debug }
    """
    try:
        data = request.get_json() or {}
        query = (data.get('query') or '').strip()
        if not query:
            return jsonify({"success": False, "error": "No query provided"}), 400

        try:
            from yt_dlp import YoutubeDL  # type: ignore
        except Exception as e:
            return jsonify({"success": False, "error": "yt-dlp not installed. pip install yt-dlp"}), 500

        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch1',
            'skip_download': True,
            'headers': _COMMON_UPSTREAM_HEADERS,
        }
        title = query
        duration = None
        audio_url = None
        watch_url = None
        thumbnail = None
        debug = {}

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            entry = None
            if 'entries' in info and info['entries']:
                entry = info['entries'][0]
            else:
                entry = info
            title = entry.get('title') or title
            duration = entry.get('duration')
            watch_url = entry.get('webpage_url')
            thumbnail = entry.get('thumbnail')
            debug['id'] = entry.get('id')
            # pick bestaudio format url
            formats = entry.get('formats') or []
            debug['format_count'] = len(formats)
            best_audio = None
            for fmt in formats:
                if fmt.get('acodec') != 'none' and (fmt.get('vcodec') in (None, 'none')):
                    if not best_audio or (fmt.get('abr') or 0) > (best_audio.get('abr') or 0):
                        best_audio = fmt
            if best_audio and best_audio.get('url'):
                audio_url = best_audio['url']
                debug['chosen_fmt'] = {
                    'abr': best_audio.get('abr'),
                    'acodec': best_audio.get('acodec'),
                    'ext': best_audio.get('ext'),
                    'vcodec': best_audio.get('vcodec'),
                }
            else:
                if formats:
                    audio_url = formats[0].get('url')

        if not audio_url:
            return jsonify({"success": False, "error": "No audio stream found", "debug": debug}), 502

        proxied = f"/api/stream?src={requests.utils.requote_uri(audio_url)}"
        mp3_url = None
        if shutil.which('ffmpeg'):
            mp3_url = f"/api/stream-mp3?src={requests.utils.requote_uri(audio_url)}"
        else:
            debug['ffmpeg'] = 'not found on PATH'

        return jsonify({
            "success": True,
            "title": title,
            "url": proxied,
            "duration": duration,
            "watch_url": watch_url,
            "thumbnail": thumbnail,
            "mp3_url": mp3_url,
            "debug": debug
        })
    except Exception as e:
        app.logger.error(f"[play-music] error: {e}")
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/daily-tasks', methods=['POST'])
def api_daily_tasks():
    """Process daily task commands. Currently supports 'play ...' music queries.

    Returns JSON compatible with the music player handler.
    """
    try:
        data = request.get_json() or {}
        command = (data.get('command') or '').strip()
        if not command:
            return jsonify({"success": False, "error": "No command provided"}), 400

        lower = command.lower()
        if 'play' in lower:
            # extract query after 'play'
            idx = lower.find('play')
            q = command[idx + len('play'):].strip() or command
            # reuse play-music logic
            with app.test_request_context('/api/play-music', method='POST', json={'query': q}):
                resp = api_play_music()
            # If resp is a tuple (response, status), pick first
            if isinstance(resp, tuple):
                payload = resp[0].get_json() if hasattr(resp[0], 'get_json') else None
                status = resp[1]
            else:
                payload = resp.get_json() if hasattr(resp, 'get_json') else None
                status = 200
            if payload and payload.get('success'):
                return jsonify(payload)
            # Fall back to generic acknowledgement
            return jsonify({"success": True, "title": q, "url": None, "duration": None})

        # Not recognized; acknowledge
        return jsonify({"success": True, "message": "Command noted."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def generate_ai_response(message, conversation_history):
    """Generate AI response based on message and conversation history"""
    message_lower = message.lower()
    
    if 'help' in message_lower or 'assist' in message_lower:
        return (
            "I'm here to help! I can assist you with accessibility features, daily tasks, government schemes, legal rights, and more. "
            "To explore features: open the Dashboard and try: <a href='/welfare_schemes'>Welfare Schemes</a>, <a href='/legal_rights'>Legal Rights</a>, <a href='/camera_navigation'>Camera Navigation</a>. "
            "You can also ask me specific questions like ‘set a reminder at 6 PM’."
        )
    elif 'accessibility' in message_lower:
        return (
            "Accessibility features include voice commands, text-to-speech, sign language recognition, camera navigation, and screen reader support. "
            "In this app, try: <a href='/camera_navigation'>Camera Navigation</a> for object/text detection, and the quick actions below the chat. "
            "On your device, open Settings → Accessibility to enable screen reader, magnifier, captions, and voice control."
        )
    elif 'government' in message_lower or 'scheme' in message_lower:
        return (
            "I can help you find government welfare schemes for disabled individuals. "
            "Go to <a href='/welfare_schemes'>Welfare Schemes</a> to browse by category or search. "
            "Have your disability certificate and ID handy; tell me your state or need and I’ll guide you."
        )
    elif 'legal' in message_lower or 'right' in message_lower:
        return (
            "I can provide information about your legal rights as a disabled person. "
            "Open <a href='/legal_rights'>Legal Rights</a> for an overview and resources. "
            "If you describe your situation, I can suggest concrete next steps."
        )
    elif 'music' in message_lower or 'play' in message_lower:
        return (
            "I can help you play music! Tell me a song, artist, or mood (e.g., ‘play relaxing music’). "
            "If you’re using a player, I can provide commands or playlists to try."
        )
    elif 'reminder' in message_lower or 'remind' in message_lower or 'alarm' in message_lower:
        return (
            "I can help you set reminders. Just say ‘remind me to take medicine at 6 PM’. "
            "Be specific with time and note. I’ll confirm and notify you at the time."
        )
    elif 'camera' in message_lower or 'navigation' in message_lower:
        return (
            "I can help with camera navigation! Open <a href='/camera_navigation'>Camera Navigation</a> to start object detection and text reading. "
            "Tip: use good lighting and headphones for clearer guidance."
        )
    else:
        return (
            f"I understand you're asking about '{message}'. "
            f"If this relates to features here, try these: <a href='/welfare_schemes'>Welfare Schemes</a>, <a href='/legal_rights'>Legal Rights</a>, <a href='/camera_navigation'>Camera Navigation</a>. "
            f"Or tell me more details and I’ll guide you step‑by‑step."
        )

def generate_generic_response(message: str) -> str:
    """Produce a helpful, domain-agnostic response without external APIs.

    This includes some topic-aware answers (e.g., accessibility) and an
    improved general fallback that is more than just a template.
    """
    text = (message or '').strip()
    lower = text.lower()

    # Topic-aware responses with actionable directions
    if 'accessibility' in lower or 'accessible' in lower or 'a11y' in lower:
        return (
            "Accessibility features you can use today:<br>"
            "- Screen readers: Narrator (Windows), VoiceOver (iOS/macOS), TalkBack (Android).<br>"
            "- Voice control: Dictation and app control (Windows Voice Access, macOS Voice Control, Google Assistant, Siri).<br>"
            "- Captions: Live captions on Windows/Android; enable captions in apps like YouTube/Meet/Zoom.<br>"
            "- Magnification & contrast: Display magnifier, zoom, color filters, high‑contrast themes.<br>"
            "- Keyboard navigation and alternative input: Switch control, on‑screen keyboard, eye‑tracking.<br><br>"
            "Try these here: <a href='/camera_navigation'>Camera Navigation</a> for object/text detection; use the chat’s quick actions. "
            "On your device: Settings → Accessibility to enable screen reader, captions, and zoom."
        )

    if 'government' in lower or 'scheme' in lower:
        return (
            "Government welfare schemes overview:<br>"
            "- Types: financial aid, education, healthcare, assistive devices, employment quotas.<br>"
            "- How to proceed: Open <a href='/welfare_schemes'>Welfare Schemes</a> to browse/search; keep disability certificate, ID, and bank details ready.<br>"
            "- Tip: Tell me your state and need (e.g., education, device) for tailored guidance."
        )

    if 'legal' in lower or 'right' in lower:
        return (
            "Legal rights (general guidance):<br>"
            "- Non‑discrimination and reasonable accommodations at work/school.<br>"
            "- Digital and physical accessibility requirements.<br>"
            "- Action: Visit <a href='/legal_rights'>Legal Rights</a> for resources; describe your case for step‑by‑step help."
        )

    if 'remind' in lower or 'reminder' in lower or 'alarm' in lower:
        return (
            "Reminders made easy:<br>"
            "- Say: ‘Remind me to take medicine at 6 PM’. Include the time and note.<br>"
            "- I’ll confirm and schedule it, then notify you at the time."
        )

    if 'camera' in lower or 'navigation' in lower:
        return (
            "Camera navigation:<br>"
            "- Open <a href='/camera_navigation'>Camera Navigation</a> to detect objects and read text aloud.<br>"
            "- Tips: good lighting, clean lens, use headphones for audio cues."
        )

    # Question-style heuristics
    starters = [
        ('what is', 'definition'),
        ('who is', 'person'),
        ('how to', 'howto'),
        ('how do i', 'howto'),
        ('why', 'why'),
        ('when', 'when'),
        ('where', 'where'),
        ('compare', 'compare'),
        ('pros and cons', 'proscons')
    ]
    kind = None
    for prefix, k in starters:
        if lower.startswith(prefix):
            kind = k
            break

    topic = text.rstrip(' ?!.')

    if kind == 'howto':
        return (
            f"How to {topic.replace('how to', '').replace('How to', '').strip()}:<br>"
            f"1) Clarify the goal and constraints.<br>"
            f"2) Prepare tools/resources.<br>"
            f"3) Execute step‑by‑step, validating each step.<br>"
            f"4) Troubleshoot and iterate.<br>"
            f"5) Verify results with a checklist.<br>"
            f"If this relates to our app, you may also try: <a href='/welfare_schemes'>Welfare Schemes</a>, <a href='/legal_rights'>Legal Rights</a>, <a href='/camera_navigation'>Camera Navigation</a>."
        )

    if kind == 'definition' or kind == 'person':
        return (
            f"About {topic}:<br>"
            f"- Core idea: a concise explanation in plain language.<br>"
            f"- Context: where it’s used and why it matters.<br>"
            f"- Example: a short illustration.<br>"
            f"Need specifics? Share your use‑case and I’ll adapt."
        )

    if kind == 'why':
        return (
            f"Why {topic}:<br>"
            f"- Main reason and contributing factors.<br>"
            f"- Implications in practice.<br>"
            f"Tell me your context for targeted guidance."
        )

    if kind == 'compare':
        return (
            f"Comparison for {topic}:<br>"
            f"- Criteria: performance, cost, ease, flexibility, community.<br>"
            f"- Strengths and trade‑offs of each option.<br>"
            f"- Recommendation depends on constraints—share them for a concrete pick."
        )

    if kind == 'proscons':
        return (
            f"Pros and cons of {topic}:<br>"
            f"- Pros: key strengths and benefits.<br>"
            f"- Cons: limitations and risks.<br>"
            f"- Mitigations: ways to reduce downsides."
        )

    # Improved general fallback with in-app directions
    return (
        f"Here’s an overview of '{topic}':<br>"
        f"- Key concepts, practical steps, pitfalls, and a quick example.<br>"
        f"If this is about features here, try: <a href='/welfare_schemes'>Welfare Schemes</a>, <a href='/legal_rights'>Legal Rights</a>, <a href='/camera_navigation'>Camera Navigation</a>.<br>"
        f"Share goals/tools and I’ll give step‑by‑step, tailored instructions."
    )

@app.route('/media/<path:filename>')
def serve_media(filename):
    path = os.path.join(MEDIA_DIR, filename)
    if not os.path.isfile(path):
        return "Not found", 404
    return send_file(path, mimetype='audio/mpeg', conditional=True)


@app.route('/api/download-music', methods=['POST'])
def api_download_music():
    """Fallback: download best audio and convert to MP3 locally, then serve it.

    Returns JSON: { success, title, url, duration }
    """
    try:
        data = request.get_json() or {}
        query = (data.get('query') or '').strip()
        if not query:
            return jsonify({"success": False, "error": "No query provided"}), 400
        try:
            from yt_dlp import YoutubeDL  # type: ignore
        except Exception:
            return jsonify({"success": False, "error": "yt-dlp not installed"}), 500

        out_id = uuid.uuid4().hex
        out_tmpl = os.path.join(MEDIA_DIR, out_id + ".%(ext)s")
        ydl_opts = {
            'quiet': True,
            'noplaylist': True,
            'default_search': 'ytsearch1',
            'outtmpl': out_tmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'paths': {'home': MEDIA_DIR},
            'headers': _COMMON_UPSTREAM_HEADERS,
        }
        title = query
        duration = None
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            entry = info['entries'][0] if ('entries' in info and info['entries']) else info
            title = entry.get('title') or title
            duration = entry.get('duration')
        # After postprocessing, resulting file should be mp3 with our id
        mp3_path = os.path.join(MEDIA_DIR, out_id + ".mp3")
        if not os.path.isfile(mp3_path):
            # try to find any produced mp3
            for fn in os.listdir(MEDIA_DIR):
                if fn.startswith(out_id) and fn.endswith('.mp3'):
                    mp3_path = os.path.join(MEDIA_DIR, fn)
                    break
        if not os.path.isfile(mp3_path):
            return jsonify({"success": False, "error": "MP3 not produced"}), 502
        url = f"/media/{os.path.basename(mp3_path)}"
        return jsonify({"success": True, "title": title, "url": url, "duration": duration})
    except Exception as e:
        app.logger.error(f"[download-music] error: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/offline')
def offline_index():
    try:
        return send_from_directory(OFFLINE_DIR, 'index.html')
    except Exception as e:
        return f"Unable to load offline app: {e}", 500

@app.route('/offline/<path:path>')
def offline_static(path):
    try:
        return send_from_directory(OFFLINE_DIR, path)
    except Exception:
        return "Not found", 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
