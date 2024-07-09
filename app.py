from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory
from pytube import YouTube
import youtube_dl
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'static/downloads'
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
            <option value="youtube-dl">youtube-dl</option>
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
    elif method == 'youtube-dl':
        return download_with_youtube_dl(url)
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

def download_with_youtube_dl(url):
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = ydl.prepare_filename(info_dict)
            video_filename = os.path.basename(video_title)
        return redirect(url_for('downloaded_file', filename=video_filename))
    except Exception as e:
        return str(e)

@app.route('/downloads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
