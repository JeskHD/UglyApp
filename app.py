from flask import Flask, request, send_file, render_template_string, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
import requests
import shutil
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

socketio = SocketIO(app)

db = SQLAlchemy(app)

# Ensure the downloads directory exists
DOWNLOADS_DIR = 'static/uploads'
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Example model for demonstration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

@app.route('/')
def index():
    try:
        html_content = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ugly Downloader</title>
            <style>
                /* CSS styles here */
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
                                    <form action="/download" method="post">
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
        return render_template_string(html_content)
    except Exception as e:
        return f"Error rendering page: {str(e)}"

def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

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
        return handle_direct_download(url, format)
    except requests.exceptions.RequestException as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('index'))

def handle_direct_download(url, format):
    filename = url.split('/')[-1]
    if format == 'audio':
        filename += '.mp3'
    else:
        filename += '.mp4'

    filepath = os.path.join(DOWNLOADS_DIR, filename)

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return send_file_response(filepath)

def send_file_response(file_to_send):
    if os.path.exists(file_to_send):
        socketio.emit('download_complete', {'filename': os.path.basename(file_to_send)})
        return send_file(file_to_send, as_attachment=True, download_name=os.path.basename(file_to_send))
    else:
        flash("File not found after download.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
