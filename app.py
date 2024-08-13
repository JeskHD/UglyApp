import os
import subprocess
import yt_dlp
from flask import Flask, request, send_file, render_template_string, redirect, url_for, flash, current_app, send_from_directory, jsonify
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
import time  # Import time module to measure time

# Patch the standard library to make it cooperative with gevent
gevent.monkey.patch_all()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Flask-SocketIO with CORS allowed origins
socketio = SocketIO(app, cors_allowed_origins="*")
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
        /* (Your CSS styling) */
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
    <script>
        var socket = io();
        socket.on('connect', function() {
            console.log('Connected to server');
        });
        socket.on('download_complete', function(data) {
            alert('Download complete: ' + data.filename);
            location.reload();  // Reload the page after the download is complete
        });

        document.addEventListener("DOMContentLoaded", function() {
            var menuToggle = document.querySelector(".menu-toggle");
            var menu = document.querySelector(".topbar ul");

            menuToggle.addEventListener("click", function() {
                menu.classList.toggle("active");
            });

            // Show the indeterminate progress bar on form submit
            var forms = document.querySelectorAll("form");
            forms.forEach(function(form) {
                form.addEventListener("submit", function() {
                    document.querySelector('.demo-container').style.display = 'block';
                });
            });
        });
    </script>
</head>
<body>
    <div class="topbar">
        <header>
            <nav>
                <h2 class="ua">Ugly Downloader</h2>
                <div class="menu-toggle">
                    <i class="fa fa-bars"></i>
                </div>
                <ul class="menu">
                    <li>About Us</li>
                    <li>Collection</li>
                    <li>Media</li>
                    <li>FAQ</li>
                    <li>Downloader</li>
                    <div class="sp">
                        <li><i class="fa fa-twitter"></i></li>
                    </div>
                </ul>
            </nav>
        </header>
    </div>
    <div class="bimage">
        <main>
            <h1></h1>
            <section class="Wrapper">
                <article>
                    <div>
                        <h2 class="UglyStay">Stay Ugly With Our Media</h2>
                        <p class="uglydesc">Download Ugly Bros' art, music, and videos swiftly with UglyDownloader. Quality and simplicity in one click.</p>
                        <br>
                        <div class="form-container">
                            <form action="/download" method="post" enctype="multipart/form-data">
                                <div class="AllC">
                                    <input type="text" name="audio_url" placeholder="Enter audio URL" class="searchbox">
                                    <select name="audio_format" class="dropdown1">
                                        <option value="mp3">MP3</option>
                                        <option value="m4a">M4A</option>
                                    </select>
                                    <button type="submit" name="format" value="audio" class="btn1">Download Audio</button>
                                    <br>
                                    <p class="or">OR</p><br>
                                    <input type="text" name="video_url" placeholder="Enter video URL" class="searchbox">
                                    <select name="video_format" class="dropdown2">
                                        <option value="mp4">MP4</option>
                                        <option value="mov">MOV</option>
                                    </select>
                                    <button type="submit" name="format" value="video" class="btn2">Download Video</button>
                                    <br><br>
                            </form>
                            <p class="url">Enter your desired URL and let it do the trick</p>
                            <div class="message">
                                {% with messages = get_flashed_messages() %}
                                    {% if messages %}
                                        <ul class="flashes">
                                        {% for message in messages %}
                                            <li>{{ message }}</li>
                                        {% endfor %}
                                        </ul>
                                    {% endif %}
                                {% endwith %}
                            </div>
                        </div>

                        <!-- Indeterminate Progress Bar -->
                        <div class="demo-container">
                            <div class="progress-bar">
                                <div class="progress-bar-value"></div>
                            </div>
                        </div>
                    </div>
                </article>
            </section>
        </main>
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
        # Emit start_download event to client
        socketio.emit('start_download')

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

        start_time = time.time()  # Start time for download

        def progress_hook(d):
            try:
                # Initialize total_size from 'total_bytes' or 'total_bytes_estimate'
                total_size = d.get('total_bytes') or d.get('total_bytes_estimate')

                # Ensure total_size is available before proceeding
                if total_size:
                    downloaded_size = d.get('downloaded_bytes', 0)
                    progress = (downloaded_size / total_size) * 100

                    # Emit the progress to the client
                    socketio.emit('progress', {'progress': progress})

                    print(f"Total Size: {total_size}, Downloaded: {downloaded_size}, Progress: {progress}%")
                else:
                    # If total_size isn't available, handle the case appropriately
                    print("Total size not available, skipping progress update.")

                # Handle the finished status
                if d['status'] == 'finished':
                    socketio.emit('progress', {'progress': 100})
                    print("Download finished, emitting 100% progress")

            except Exception as e:
                logger.error(f"Error in progress hook: {str(e)}")

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

                    end_time = time.time()  # End time for download
                    time_taken = end_time - start_time  # Calculate total time taken
                    socketio.emit('download_complete', {'filename': os.path.basename(latest_file), 'time_taken': time_taken})
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
                    file_path = file_path.replace('.mp4', f'.mov')
                    convert_command = [
                        ffmpeg_location,
                        '-n',  # Skip overwriting existing files
                        '-i', file_path,
                        '-c:v', 'copy',
                        '-c:a', 'copy',
                        file_path.replace('.mp4', '.mov')
                    ]
                    subprocess.run(convert_command, check=True)
                    file_path = file_path.replace('.mp4', '.mov')

            if os.path.exists(file_path):
                end_time = time.time()  # End time for download
                time_taken = end_time - start_time  # Calculate total time taken
                socketio.emit('download_complete', {'filename': os.path.basename(file_path), 'time_taken': time_taken})
                return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))
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

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("Unhandled exception", exc_info=True)
    response = {
        "message": "An internal error occurred.",
        "details": str(e)
    }
    return jsonify(response), 500

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Critical error on startup: {str(e)}", exc_info=True)
