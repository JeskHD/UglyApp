from flask import Flask, request, send_from_directory, render_template_string, flash, redirect, url_for
import os
from yt_dlp import YoutubeDL
from pytube import YouTube, exceptions
from moviepy.editor import VideoFileClip
from pydub import AudioSegment

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# HTML template embedded as a string
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ugly Downloader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(to bottom, #ff5f6d, #ffc371);
            color: white;
            text-align: center;
            padding: 50px;
        }
        h1 {
            font-size: 3em;
        }
        form {
            margin: 20px auto;
            max-width: 500px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            font-size: 1.2em;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            border: none;
            border-radius: 5px;
        }
        select, button {
            padding: 10px;
            border: none;
            border-radius: 5px;
            font-size: 1em;
        }
        button {
            background-color: #333;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #555;
        }
        .converter {
            margin: 20px 0;
        }
        .divider {
            margin: 30px 0;
            font-size: 1.5em;
        }
        .flash {
            background-color: #ff4d4d;
            color: white;
            padding: 10px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Ugly Downloader</h1>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul class="flash">
        {% for category, message in messages %}
          <li>{{ message }}</li>
        {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <p>Download Ugly Bros' art, music, and videos swiftly with UglyDownloader. Quality and simplicity in one click.</p>
    <div class="converter">
        <form action="/download_audio" method="post">
            <label for="audio_url">Enter audio URL:</label>
            <input type="text" id="audio_url" name="url" placeholder="Enter audio URL" required>
            <select name="format">
                <option value="mp3">MP3</option>
                <option value="m4a">M4A</option>
            </select>
            <button type="submit">Download Audio</button>
        </form>
    </div>
    <div class="divider">OR</div>
    <div class="converter">
        <form action="/download_video" method="post">
            <label for="video_url">Enter video URL:</label>
            <input type="text" id="video_url" name="url" placeholder="Enter video URL" required>
            <select name="format">
                <option value="mp4">MP4</option>
                <option value="mov">MOV</option>
            </select>
            <button type="submit">Download Video</button>
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

def download_audio(url, format):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(UPLOAD_FOLDER, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info_dict).rsplit('.', 1)[0] + f'.{format}'
    
    return file_path

@app.route('/download_audio', methods=['POST'])
def download_audio_route():
    url = request.form['url']
    format_type = request.form['format']
    
    try:
        file_path = download_audio(url, format_type)
        return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(file_path), as_attachment=True)
    
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))

@app.route('/download_video', methods=['POST'])
def download_video_route():
    url = request.form['url']
    format_type = request.form['format']
    
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        file_path = stream.download(output_path=UPLOAD_FOLDER)
        
        video = VideoFileClip(file_path)
        converted_path = os.path.join(UPLOAD_FOLDER, f"video.{format_type}")
        video.write_videofile(converted_path, codec='libx264' if format_type == 'mov' else 'libx264')
        
        os.remove(file_path)
        return send_from_directory(app.config['UPLOAD_FOLDER'], os.path.basename(converted_path), as_attachment=True)
    
    except exceptions.VideoUnavailable:
        flash('The video is unavailable.')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
