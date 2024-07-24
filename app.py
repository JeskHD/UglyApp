import os
import json
import subprocess
from flask import Flask, request, redirect, url_for, flash, render_template_string, send_file
import logging
import redis
from urllib.parse import urlparse
from flask_socketio import SocketIO
import glob
import base64
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)

# Ensure the downloads directory exists in the user's Downloads folder
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), 'Downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Redis for storing OAuth tokens
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
r = redis.from_url(REDIS_URL)

# File to save credentials
CREDENTIALS_FILE = "twitter_credentials.json"
COOKIES_FILE = 'cookies_netscape.txt'

# Function to check if URL is valid
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

# Function to get base64 encoded image
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to get base64 encoded font
def get_base64_font(font_path):
    with open(font_path, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode('utf-8')

# Function to load cookies from file
def load_cookies(file_path):
    cookies = {}
    with open(file_path, 'r') as f:
        for line in f:
            if not line.startswith('#') and line.strip():
                parts = line.strip().split('\t')
                cookies[parts[5]] = parts[6]
    return cookies

# Route to render the home page
@app.route('/')
def index():
    try:
        background_base64 = get_base64_image('uglygif.gif')
        font_base64 = get_base64_font('PORKH___.TTF.ttf')

        html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="HTML WEB DESIGN" content="Web Design">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ugly Downloader</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <style>
        @font-face {
            font-family: 'Porkys';
            src: url(data:font/ttf;base64,{{ font_base64 }}) format('truetype');
        }
        /* Styles omitted for brevity */
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        var socket = io();
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        socket.on('download_complete', function(data) {
            alert('Download complete: ' + data.filename);
        });
    </script>
</head>
<body>
    <!-- HTML content omitted for brevity -->
</body>
</html>
        '''
        return render_template_string(html_content, background_base64=background_base64, font_base64=font_base64)
    except Exception as e:
        logger.error(f"Error rendering page: {str(e)}")
        return f"Error rendering page: {str(e)}"

# Route to handle the download request
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
        twitter_credentials = r.get("twitter_credentials")
        if not twitter_credentials:
            flash("OAuth token is missing. Please log in.")
            return redirect(url_for('oauth'))

        creds = json.loads(twitter_credentials.decode("utf-8"))

        if not os.path.exists(COOKIES_FILE):
            flash("Cookies file not found.")
            return redirect(url_for('index'))

        headers = {
            "Authorization": f"Bearer {creds['access_token']}",
            "Consumer-Key": creds["consumer_key"],
            "Consumer-Secret": creds["consumer_secret"],
            "Access-Token-Secret": creds["access_token_secret"]
        }

        # Paths to ffmpeg and ffprobe
        ffmpeg_location = '/usr/bin/ffmpeg'
        ffprobe_location = '/usr/bin/ffprobe'

        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_location,
            'ffprobe_location': ffprobe_location,
            'hls_use_mpegts': True,  # Ensure HLS processing for all formats
            'noprogress': True,  # Do not show progress bar
        }

        # Log details of the operation
        logger.debug(f"Starting download for URL: {url}")
        logger.debug(f"Using cookies file: {COOKIES_FILE}")

        if "twitter.com/i/spaces" in url or "x.com/i/spaces" in url:
            audio_format = request.form.get('audio_format', 'm4a/mp3')
            output_template = os.path.join(DOWNLOADS_DIR, '%(title)s')

            command = [
                '/root/UglyApp/venv/bin/python3', '-m', 'twspace_dl',
                '-c', COOKIES_FILE,  # Use the cookies file uploaded
                '-i', url,
                '-v'
            ]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            while True:
                output = process.stdout.readline()
                if process.poll() is not None:
                    break
                if output:
                    logger.debug(output.strip())
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
                    logger.error("File not found after download.")
                    flash("File not found after download.")
                    return redirect(url_for('index'))
            else:
                logger.error("Error during the download process.")
                flash("Error during the download process.")
                return redirect(url_for('index'))

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {str(e)}")
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
        flash(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        flash(f"An unexpected error occurred: {str(e)}")
        return redirect(url_for('index'))

    return redirect(url_for('index'))  # Ensure there is a return statement in all paths

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
