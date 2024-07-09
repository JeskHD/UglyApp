from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash
import os
from yt_dlp import YoutubeDL

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages
DOWNLOAD_FOLDER = 'static/downloads'
COOKIES_FILE = 'cookies_netscape.txt'  # Path to your cookies file
FFMPEG_PATH = 'ffmpeg'  # Path to your ffmpeg binaries relative to the project root

app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Downloader</title>
</head>
<body>
    <h1>Download YouTube Video</h1>
    <form action="/download" method="post">
        <label for="url">YouTube Video URL:</label>
        <input type="url" id="url" name="url" required>
        <br>
        <label for="method">Download Method:</label>
        <select id="method" name="method">
            <option value="pytube">PyTube</option>
            <option value="yt-dlp">yt-dlp</option>
        </select>
        <br>
        <button type="submit">Download</button>
    </form>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/download', methods=['POST'])
def download_video():
    url = request.form['url']
    method = request.form['method']

    if method == 'pytube':
        return download_with_pytube(url)
    elif method == 'yt-dlp':
        return download_with_ytdlp(url)
    else:
        return "Invalid download method."

def download_with_pytube(url):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        out_file = video.download(output_path=app.config['DOWNLOAD_FOLDER'])
        return redirect(url_for('downloaded_file', filename=os.path.basename(out_file)))
    except Exception as e:
        return str(e)

def download_with_ytdlp(url):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
            'ffmpeg_location': FFMPEG_PATH,  # Specify the path to ffmpeg binaries
            'cookiefile': COOKIES_FILE  # Adding the path to the cookies file
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = ydl.prepare_filename(info_dict)
            video_filename = os.path.basename(video_title)
        return redirect(url_for('downloaded_file', filename=video_filename))
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))

@app.route('/downloads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
