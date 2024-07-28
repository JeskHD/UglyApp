import os
from flask import Flask, request, send_file, jsonify, abort
import subprocess

app = Flask(__name__)

# Ensure the downloads directory exists
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), 'UglyApp')
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@app.route('/download', methods=['POST'])
def download_file():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400
        
        output_path = os.path.join(DOWNLOADS_DIR, 'bar.mp3')
        
        # Download the audio using ffmpeg
        subprocess.run(['ffmpeg', '-i', url, '-b:a', '192K', '-vn', output_path], check=True)
        
        return send_file(output_path, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
