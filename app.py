import os
import subprocess
import yt_dlp
from flask import Flask, request, send_file, render_template_string, redirect, url_for, flash, current_app, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import sqlalchemy as sa
import glob
import base64
import logging
from tqdm import tqdm
import gevent
import gevent.monkey

# Patch the standard library to make it cooperative with gevent
gevent.monkey.patch_all()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Flask-SocketIO with CORS allowed origins
socketio = SocketIO(app, cors_allowed_origins="http://167.172.128.150")
db = SQLAlchemy(app)

# Ensure the downloads directory exists in the user's Downloads folder
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), 'Downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Example model for demonstration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_base64_font(font_path):
    with open(font_path, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode('utf-8')

@app.route('/')
def index():
    try:
        background_base64 = get_base64_image('uglygif.gif')
        logo_base64 = get_base64_image('uglylogo.png')
        font_base64 = get_base64_font('PORKH___.TTF.ttf')

        html_content = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ugly Downloader</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <style>
                @font-face {
                    font-family: 'Porkys';
                    src: url(data:font/ttf;base64,{{ font_base64 }}) format('truetype');
                }
                body {
                    font-family: "Poppins", sans-serif;
                }
                .progress {
                    background-color: #e0e0e0;
                    border-radius: 13px;
                    padding: 3px;
                    margin-top: 20px;
                }
                .progress-bar {
                    background-color: #76c7c0;
                    width: 0%;
                    height: 25px;
                    border-radius: 10px;
                    text-align: center;
                    line-height: 25px;
                    color: white;
                }
            </style>
            <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
            <script type="text/javascript">
                localStorage.debug = 'socket.io-client:*'; // Enable debug logs in the browser
                document.addEventListener('DOMContentLoaded', function() {
                    var socket = io.connect('http://167.172.128.150', {
                        transports: ['websocket'],  // Use only WebSocket transport
                        rejectUnauthorized: false  // Disable SSL verification if needed
                    });

                    socket.on('connect', function() {
                        console.log('Connected to server');
                        document.getElementById('status').innerHTML = 'Connected to server';
                    });

                    socket.on('test_response', function(data) {
                        console.log('Response from server:', data);
                        document.getElementById('response').innerHTML = 'Response from server: ' + data.message;
                    });

                    document.getElementById('sendButton').addEventListener('click', function() {
                        console.log('Sending test message to server');
                        socket.emit('test_message', {'data': 'Hello from client'});
                    });

                    socket.on('disconnect', function() {
                        console.error('Disconnected from server');
                        document.getElementById('status').innerHTML = 'Disconnected from server';
                    });

                    socket.on('connect_error', function(error) {
                        console.error('Connection error:', error);
                        document.getElementById('status').innerHTML = 'Connection error: ' + error;
                    });

                    socket.on('connect_timeout', function() {
                        console.error('Connection timed out');
                        document.getElementById('status').innerHTML = 'Connection timed out';
                    });

                    socket.on('reconnect_attempt', function() {
                        console.log('Attempting to reconnect...');
                        document.getElementById('status').innerHTML = 'Attempting to reconnect...';
                    });

                    socket.on('reconnect_failed', function() {
                        console.error('Reconnection failed');
                        document.getElementById('status').innerHTML = 'Reconnection failed';
                    });

                    socket.on('progress', function(data) {
                        var progress = data.progress;
                        document.getElementById("progressBar").style.width = progress + "%";
                        document.getElementById("progressBar").innerText = Math.round(progress) + "%";
                    });

                    socket.on('download_complete', function(data) {
                        alert('Download complete: ' + data.filename);
                    });
                });
            </script>
        </head>
        <body>
            <h1>Ugly Downloader</h1>
            <p id="status">Not connected</p>
            <button id="sendButton">Send Test Message</button>
            <p id="response">No response yet</p>
            <div class="progress">
                <div id="progressBar" class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100">0%</div>
            </div>
        </body>
        </html>
        '''
        return render_template_string(html_content, background_base64=background_base64, font_base64=font_base64)
    except Exception as e:
        logger.error(f"Error rendering page: {str(e)}")
        return f"Error rendering page: {str(e)}"

@socketio.on('test_message')
def handle_test_message(json):
    try:
        logger.debug(f'Received test message: {json}')
        emit('test_response', {'message': 'Hello from server'})
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("Unhandled exception", exc_info=True)
    response = {
        "message": "An internal error occurred.",
        "details": str(e)
    }
    return jsonify(response), 500

@app.route('/download', methods=['POST'])
def download():
    audio_url = request.form.get('audio_url')
    video_url = request.form.get('video_url')
    format = request.form['format']
    url = audio_url if format == 'audio' else video_url
    
    if not is_valid_url(url):
        flash("Invalid URL. Please enter a valid URL.")
        return redirect(url_for('index'))

    try:
        # Paths to ffmpeg and ffprobe
        ffmpeg_location = '/usr/bin/ffmpeg'
        ffprobe_location = '/usr/bin/ffprobe'

        # Set the cookie file path based on user input
        cookie_file = None
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_location,
            'ffprobe_location': ffprobe_location,
            'hls_use_mpegts': True,  # Ensure HLS processing for all formats
            'nooverwrites': True,  # Skip existing files instead of overwriting
        }

        def progress_hook(d):
            if d['status'] == 'downloading':
                total_size = d.get('total_bytes', 0)
                downloaded_size = d.get('downloaded_bytes', 0)
                if total_size > 0:
                    progress = (downloaded_size / total_size) * 100
                    print(f"Emitting progress: {progress}%")
                    socketio.emit('progress', {'progress': progress})
            elif d['status'] == 'finished':
                print("Download finished, emitting 100% progress")
                socketio.emit('progress', {'progress': 100})
        
        ydl_opts['progress_hooks'] = [progress_hook]

        # Handle Twitter Spaces downloads separately
        if "twitter.com/i/spaces" in url or "x.com/i/spaces" in url:
            cookie_file = 'cookies_netscape.txt'
            audio_format = request.form.get('audio_format', 'm4a/mp3')
            output_template = os.path.join(DOWNLOADS_DIR, '%(title)s')
            
            command = [
                '/root/UglyApp/venv/bin/twspace_dl',  # Use the full path to twspace_dl
                '-i', url,
                '-c', cookie_file,
                '-o', output_template
            ]
            
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            while True:
                output = process.stdout.readline()
                if process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    socketio.emit('eta', {'data': output.strip()})

            process.wait()

            if process.returncode == 0:
                # Find the most recently modified file in the DOWNLOADS_DIR
                list_of_files = glob.glob(os.path.join(DOWNLOADS_DIR, '*'))
                latest_file = max(list_of_files, key=os.path.getmtime)
                
                if os.path.exists(latest_file):
                    if audio_format == 'mp3' and latest_file.endswith('.m4a'):
                        # Convert to MP3
                        mp3_file = latest_file.replace('.m4a', '.mp3')
                        convert_command = [
                            ffmpeg_location,
                            '-n',  # Skip overwriting existing files
                            '-i', latest_file,
                            '-codec:a', 'libmp3lame',
                            '-qscale:a', '2',
                            mp3_file
                        ]
                        subprocess.run(convert_command, check=True)
                        latest_file = mp3_file

                    socketio.emit('download_complete', {'filename': os.path.basename(latest_file)})
                    return send_file(latest_file, as_attachment=True, download_name=os.path.basename(latest_file))
                else:
                    flash("File not found after download.")
                    return redirect(url_for('index'))
            else:
                flash("Error during the download process.")
                return redirect(url_for('index'))
        
        # Use cookies for YouTube downloads
        elif 'youtube.com' in url:
            cookie_file = 'youtube_cookies.txt'  # Update with your actual path
            ydl_opts.update({
                'cookiefile': cookie_file,
                'username': 'oauth2',  # Comment this line if not using OAuth
                'password': '',  # Comment this line if not using OAuth
            })

        # Use cookies for SoundCloud downloads
        elif 'soundcloud.com' in url:
            cookie_file = 'soundcloud_cookies.txt'  # Update with your actual path
            ydl_opts.update({
                'cookiefile': cookie_file,
            })
        
        # Determine if downloading audio or video
        if format == 'audio':
            audio_format = request.form['audio_format']
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': '192',
                }]
            })
        else:
            video_format = request.form['video_format']
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4'
            })

        # Download and process using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)

            if format == 'audio':
                file_path = file_path.replace('.webm', f'.{audio_format}').replace('.opus', f'.{audio_format}')
            else:
                if video_format == 'mov':
                    file_path = file_path.replace('.mp4', f'.mp4')
                else:
                    file_path = file_path.replace('.mp4', f'.{video_format}').replace('.m4a', f'.{video_format}')
                
            if os.path.exists(file_path):
                if format == 'audio' and audio_format == 'mp3':
                    mp3_file = file_path.replace('.m4a', '.mp3')
                    convert_command = [
                        ffmpeg_location,
                        '-n',  # Skip overwriting existing files
                        '-i', file_path,
                        '-codec:a', 'libmp3lame',
                        '-qscale:a', '2',
                        mp3_file
                    ]
                    subprocess.run(convert_command, check=True)
                    file_to_send = mp3_file
                elif format == 'video' and video_format == 'mov':
                    mov_file = file_path.replace('.mp4', '.mov')
                    convert_command = [
                        ffmpeg_location,
                        '-n',  # Skip overwriting existing files
                        '-i', file_path,
                        '-c:v', 'copy',
                        '-c:a', 'copy',
                        mov_file
                    ]
                    subprocess.run(convert_command, check=True)
                    file_to_send = mov_file
                else:
                    file_to_send = file_path

                socketio.emit('download_complete', {'filename': os.path.basename(file_to_send)})
                return send_file(file_to_send, as_attachment=True, download_name=os.path.basename(file_to_send))
            else:
                flash("File not found after download.")
                return redirect(url_for('index'))
    except subprocess.CalledProcessError as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))
    except yt_dlp.utils.DownloadError as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        flash(f"An unexpected error occurred: {str(e)}")
        return redirect(url_for('index'))

    return redirect(url_for('index'))  # Ensure there is a return statement in all paths

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def upload(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(uploads, filename)

# Database initialization logic for Render
engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
inspector = sa.inspect(engine)
if not inspector.has_table("user"):
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.logger.info('Initialized the database!')
else:
    app.logger.info('Database already contains the users table.')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
