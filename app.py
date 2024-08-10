import os
import subprocess
import yt_dlp
from flask import Flask, request, send_file, render_template_string, redirect, url_for, flash, current_app, send_from_directory
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import urlparse
import sqlalchemy as sa
import glob
import base64
import logging
from tqdm import tqdm

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)
db = SQLAlchemy(app)

DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), 'Downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ugly Downloader</title>
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
                    padding-top: 100px;
                }
                .Wrapper {
                    text-align: center;
                    padding: 20px;
                }
                .UglyStay {
                    color: rgb(255, 136, 237);
                    font-size: 50px;
                    font-weight: 800;
                    font-style: italic;
                    margin: 0 20px;
                    text-align: center;
                    width: 100%;
                }
                .uglydesc {
                    color: whitesmoke;
                    margin: 20px 10px;
                    font-size: 18px;
                    text-align: center;
                    width: 100%;
                }
                .form-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    margin-top: 20px;
                    flex-wrap: wrap;
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
                    padding-left: 20px;
                }
                .btn1, .btn2 {
                    height: 38px;
                    border-radius: 0 50px 50px 0;
                    padding: 0 7px;
                    background-color: #fa50d3;
                    color: white;
                    border: none;
                    cursor: pointer;
                    font-family: "Poppins", sans-serif;
                }
                .log-area {
                    width: 100%;
                    height: 300px;
                    margin-top: 20px;
                    padding: 10px;
                    border: 1px solid #ccc;
                    background-color: #f0f0f0;
                    overflow-y: scroll;
                    white-space: pre-wrap;
                    font-family: monospace;
                }
            </style>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.min.js"></script>
            <script>
                var socket = io();
                socket.on('connect', function() {
                    console.log('Connected to server');
                });

                socket.on('log', function(data) {
                    var logArea = document.getElementById('log-area');
                    logArea.textContent += data.message + '\\n';
                    logArea.scrollTop = logArea.scrollHeight; // Auto-scroll to the bottom
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
                    </nav>
                </header>
            </div>
            <div class="bimage">
                <main>
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
                                            <button type="submit" name="format" value="audio" class="btn1">Download Audio</button>
                                            <br>
                                            <p class="or">OR</p><br>
                                            <input type="text" name="video_url" placeholder="Enter video URL" class="searchbox">
                                            <button type="submit" name="format" value="video" class="btn2">Download Video</button>
                                            <br><br>
                                        </div>
                                    </form>
                                    <div id="log-area" class="log-area"></div>
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
        ffmpeg_location = '/usr/bin/ffmpeg'
        ffprobe_location = '/usr/bin/ffprobe'

        cookie_file = None
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOADS_DIR, '%(title)s.%(ext)s'),
            'ffmpeg_location': ffmpeg_location,
            'ffprobe_location': ffprobe_location,
            'hls_use_mpegts': True,
            'nooverwrites': True,
        }

        with tqdm(total=100, desc="Processing", unit="step") as pbar:
            if "twitter.com/i/spaces" in url or "x.com/i/spaces" in url:
                cookie_file = 'cookies_netscape.txt'
                audio_format = request.form.get('audio_format', 'm4a/mp3')
                output_template = os.path.join(DOWNLOADS_DIR, '%(title)s')
                
                command = [
                    '/root/UglyApp/venv/bin/twspace_dl',
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
                        socketio.emit('log', {'message': output.strip()})
                        pbar.update(10)

                process.wait()

                if process.returncode == 0:
                    list_of_files = glob.glob(os.path.join(DOWNLOADS_DIR, '*'))
                    latest_file = max(list_of_files, key=os.path.getmtime)
                    
                    if os.path.exists(latest_file):
                        if audio_format == 'mp3' and latest_file.endswith('.m4a'):
                            mp3_file = latest_file.replace('.m4a', '.mp3')
                            convert_command = [
                                ffmpeg_location,
                                '-n',
                                '-i', latest_file,
                                '-codec:a', 'libmp3lame',
                                '-qscale:a', '2',
                                mp3_file
                            ]
                            subprocess.run(convert_command, check=True)
                            latest_file = mp3_file

                        socketio.emit('download_complete', {'filename': os.path.basename(latest_file)})
                        pbar.update(100)
                        return send_file(latest_file, as_attachment=True, download_name=os.path.basename(latest_file))
                    else:
                        flash("File not found after download.")
                        return redirect(url_for('index'))
                else:
                    flash("Error during the download process.")
                    return redirect(url_for('index'))
            
            elif 'youtube.com' in url:
                cookie_file = 'youtube_cookies.txt'
                ydl_opts.update({
                    'cookiefile': cookie_file,
                    'username': 'oauth2',
                    'password': '',
                })

            elif 'soundcloud.com' in url:
                cookie_file = 'soundcloud_cookies.txt'
                ydl_opts.update({
                    'cookiefile': cookie_file,
                })
            
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
                            '-n',
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
                            '-n',
                            '-i', file_path,
                            '-c:v', 'copy',
                            '-c:a', 'copy',
                            mov_file
                        ]
                        subprocess.run(convert_command, check=True)
                        file_to_send = mov_file
                    else:
                        file_to_send = file_path

                    socketio.emit('log', {'message': f"Download complete: {os.path.basename(file_to_send)}"})
                    pbar.update(100)
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

    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
