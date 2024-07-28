import os
import subprocess
from flask import Flask, request, send_file, jsonify

app = Flask(__name__)

# Ensure the downloads directory exists
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), 'Downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@app.route('/')
def index():
    return '''
    <form action="/download" method="post">
        <input type="text" name="url" placeholder="Enter m3u8 URL">
        <input type="submit" value="Download">
    </form>
    '''

@app.route('/download', methods=['POST'])
def download_file():
    url = request.form['url']
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    output_path = os.path.join(DOWNLOADS_DIR, 'bar.mp3')
    
    try:
        # Download the audio using ffmpeg
        result = subprocess.run(
            ['ffmpeg', '-i', url, '-b:a', '192K', '-vn', output_path],
            capture_output=True,
            text=True,
            check=True
        )
        return send_file(output_path, as_attachment=True, download_name='bar.mp3')
    except subprocess.CalledProcessError as e:
        error_message = e.stderr
        return jsonify({'error': error_message}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
