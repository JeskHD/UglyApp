from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash
import os
from yt_dlp import YoutubeDL
from pytube import YouTube
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages
DOWNLOAD_FOLDER = 'static/downloads'
COOKIES_FILE = 'cookies_netscape.txt'  # Path to your cookies file

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
        <label for="format">Select Format:</label>
        <select id="format" name="format">
            <option value="mp4">MP4</option>
            <option value="mov">MOV</option>
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
    format = request.form['format']

    if not url or not method or not format:
        flash('All fields are required.')
        return redirect(url_for('index'))

    if method == 'pytube':
        return download_with_pytube(url, format)
    elif method == 'yt-dlp':
        return download_with_ytdlp(url, format)
    else:
        flash('Invalid download method.')
        return redirect(url_for('index'))

def download_with_pytube(url, format):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        out_file = video.download(output_path=app.config['DOWNLOAD_FOLDER'])
        if format == 'mov':
            out_file = convert_to_mov(out_file)
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], os.path.basename(out_file), as_attachment=True)
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))

def download_with_ytdlp(url, format):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
            'cookiefile': COOKIES_FILE  # Adding the path to the cookies file
        }
        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            video_title = ydl.prepare_filename(info_dict)
            video_filename = os.path.basename(video_title).rsplit('.', 1)[0] + '.mp4'
        
        if format == 'mov':
            video_filename = convert_to_mov(video_filename)
        
        return send_from_directory(app.config['DOWNLOAD_FOLDER'], video_filename, as_attachment=True)
    except Exception as e:
        flash(f'An error occurred: {str(e)}')
        return redirect(url_for('index'))

def convert_to_mov(filepath):
    try:
        clip = VideoFileClip(filepath)
        new_filepath = filepath.rsplit('.', 1)[0] + '.mov'
        clip.write_videofile(new_filepath, codec='libx264', audio_codec='aac')
        clip.close()
        os.remove(filepath)
        return new_filepath
    except Exception as e:
        flash(f'An error occurred during conversion: {str(e)}')
        return filepath

@app.route('/downloads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
