import os
import subprocess
from flask import Flask, request, send_file, jsonify
import logging
import time

app = Flask(__name__)

# Ensure the downloads directory exists
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), 'Downloads')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

    output_path = os.path.join(DOWNLOADS_DIR, 'twitter-spaces-recording.mp3')

    try:
        start_time = time.time()
        # Attempt to download audio using ffmpeg
        result = subprocess.run(
            ['ffmpeg', '-i', url, '-vn', '-acodec', 'libmp3lame', '-b:a', '192k', output_path],
            capture_output=True,
            text=True,
            timeout=600  # Increase the timeout here
        )
        end_time = time.time()
        elapsed_time = end_time - start_time

        if result.returncode != 0:
            # Log the stderr for debugging purposes
            logger.error(result.stderr)
            # Check for specific error message indicating no audio stream
            if "Output file does not contain any stream" in result.stderr:
                return jsonify({'error': 'No audio stream found in the provided URL'}), 400

            return jsonify({'error': result.stderr}), 500

        return send_file(output_path, as_attachment=True, download_name='twitter-spaces-recording.mp3'), {'X-Elapsed-Time': elapsed_time}
    except subprocess.CalledProcessError as e:
        error_message = e.stderr
        logger.error(error_message)
        return jsonify({'error': error_message}), 500
    except subprocess.TimeoutExpired as e:
        logger.error("Download process timed out")
        return jsonify({'error': 'Download process timed out'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
