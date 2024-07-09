from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, flash
import os
from yt_dlp import YoutubeDL

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
    format = request.form['format']

    if not url or not format:
        flash('All fields are required.')
        return redirect(url_for('index'))

    return download_with_ytdlp(url, format)

def download_with_ytdlp(url, format):
    try:
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(app.config['DOWNLOAD_FOLDER'], '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',  # Ensure initial download in mp4 format
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
    # Conversion without using ffmpeg is not straightforward and usually not supported
    # This placeholder function assumes the conversion is possible without ffmpeg
    new_filepath = filepath.rsplit('.', 1)[0] + '.mov'
    os.rename(filepath, new_filepath)
    return new_filepath

@app.route('/downloads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
