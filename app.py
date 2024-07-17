import os
import sys
import subprocess
import yt_dlp
from flask import Flask, request, send_file, render_template_string, redirect, url_for, flash, current_app, send_from_directory, jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import sqlalchemy as sa
import glob
from collections.abc import MutableMapping

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)
db = SQLAlchemy(app)

# Ensure the downloads directory exists
DOWNLOADS_DIR = '/opt/render/Downloads'
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Example model for demonstration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

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
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }
                body {
                    font-family: "Poppins", sans-serif;
                    width: 100%;
                    overflow-x: hidden;
                }
                .topbar {
                    font-family: "Montserrat", "Poppins", "Avenir";
                    width: 100%;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 10px 50px;
                    background: rgba(0, 0, 0, 0.5);
                    position: absolute;
                    top: 0;
                    z-index: 1000;
                }
                .topbar nav {
                    display: flex;
                    align-items: center;
                    width: 100%;
                }
                .topbar .menu-toggle {
                    display: none;
                    font-size: 24px;
                    color: white;
                    cursor: pointer;
                    position: absolute;
                    right: 40px;
                }
                .topbar ul {
                    list-style-type: none;
                    padding: 0;
                    margin: 0;
                    display: flex;
                    gap: 20px;
                    position: absolute;
                    right: 50px;
                }
                .topbar ul li {
                    color: white;
                }
                .topbar ul li:hover {
                    color: rgb(255, 120, 223);
                    cursor: pointer;
                }
                .poppins-medium-italic {
                    font-family: "Poppins", sans-serif;
                    font-weight: 500;
                    font-style: italic;
                }
                .topbar img {
                    height: 65px;
                    width: auto;
                    position: relative;
                    top: 2px.
                }
                .bimage {
                    background: linear-gradient(rgba(255, 7, 156, 0.585), rgba(104, 97, 97, 0.5)), url("data:image/gif;base64,{{ background_base64 }}");
                    height: 800px;
                    width: 100%;
                    background-repeat: no-repeat;
                    background-position: center;
                    background-size: cover;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                    padding-top: 100px; /* Adjusted to move content closer to the topbar */
                }
                .Wrapper {
                    text-align: center;
                    padding: 20px.
                }
                .UglyStay {
                    color: rgb(255, 136, 237);
                    font-size: 50px;
                    font-weight: 800;
                    font-style: italic;
                    margin: 0 20px;
                    text-align: center;
                    width: 100%.
                }
                .uglydesc {
                    color: whitesmoke;
                    margin: 20px 10px;
                    font-size: 18px;
                    text-align: center;
                    width: 100%.
                }
                .form-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    margin-top: 20px;
                    flex-wrap: wrap.
                }
                .searchbox {
                    width: 300px;
                    height: 40px;
                    background-color: black;
                    border-radius: 50px 0 0 50px;
                    color: white;
                    font-family: "Poppins", sans-serif;
                    text-align: center;
                    border: none;
                    padding-left: 20px.
                }
                .searchbox:hover {
                    border: 1px solid #ff78df.
                }
                .dropdown1, .dropdown2 {
                    height: 38px;
                    border-radius: 0;
                    padding: 0 9px;
                    border: none;
                    font-family: "Poppins", sans-serif;
                    background-color: #ff78df;
                    color: white.
                }
                .btn1, .btn2 {
                    height: 38px;
                    border-radius: 0 50px 50px 0;
                    padding: 0 7px;
                    background-color: #fa50d3;
                    color: white;
                    border: none;
                    cursor: pointer;
                    font-family: "Poppins", sans-serif.
                }
                .btn1:active, .btn2:active {
                    color: #fb85df;
                    background-color: #f8a1e4.
                }
                .btn1:hover, .btn2:hover {
                    background-color: #e767c7.
                }
                .or {
                    position: relative;
                    top: 15px;
                    color: white;
                    font-size: 18px;
                    margin: 10px 0.
                }
                .url {
                    text-shadow: 0px 3px 5px 0 #c255a7;
                    color: white;
                    font-size: 14px;
                    margin-top: 10px;
                    width: 100%;
                    text-align: center.
                }
                .sp li:hover {
                    color: #1d9bf0 !important.
                }
                .ua {
                    font-family: 'Porkys';
                    color: #f50da1;
                    font-size: 40px;
                    text-shadow: 1px 1px 2px #27f1e6.
                }
                .flashes {
                    color: red;
                    list-style: none;
                    text-align: center;
                    margin-top: 10px.
                }
                /* Responsive Design */
                @media (max-width: 800px) {
                    .topbar {
                        flex-direction: row;
                        align-items: center;
                        padding: 10px 10px.
                    }
                    .topbar .menu-toggle {
                        display: block.
                    }
                    .topbar ul {
                        display: none;
                        flex-direction: column;
                        align-items: center;
                        width: 100%;
                        margin-top: 10px.
                    }
                    .topbar ul.active {
                        display: flex;
                        font-size: 10px;
                        top: 11px;
                        border: 1px solid white;
                        flex-direction: column;
                        position: absolute;
                        background-color: rgba(0, 0, 0, 0.8);
                        right: 10px;
                        top: 60px;
                        width: 200px;
                        padding: 10px.
                    }
                    .topbar h2 {
                        font-size: 24px.
                    }
                    .UglyStay {
                        font-size: 30px;
                        margin-top: 80px;
                        text-align: center.
                    }
                    .uglydesc {
                        font-size: 16px;
                        margin: 20px 20px;
                        text-align: center.
                    }
                    .form-container {
                        flex-direction: column;
                        align-items: center.
                    }
                    .searchbox, .dropdown1, .dropdown2, .btn1, .btn2 {
                        width: 100%;
                        margin-bottom: 10px.
                    }
                    .or {
                        top: 0;
                        margin: 10px 0.
                    }
                    .url {
                        margin-top: 20px;
                        text-align: center.
                    }
                }
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
        return f"Error rendering page: {str(e)}"

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

        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_location,
            'ffprobe_location': ffprobe_location,
            'cookiefile': 'cookies_netscape.txt',
            'hls_use_mpegts': True  # Ensure HLS processing for all formats
        }
        
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
