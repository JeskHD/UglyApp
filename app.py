from flask import Flask, send_from_directory, safe_join, abort
import os

app = Flask(__name__)

# Define the directory where your files are stored
DOWNLOAD_DIRECTORY = os.path.expanduser("~/UglyApp")

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Ensure the filename is safe and within the download directory
        file_path = safe_join(DOWNLOAD_DIRECTORY, filename)
        
        if os.path.exists(file_path):
            return send_from_directory(DOWNLOAD_DIRECTORY, filename, as_attachment=True)
        else:
            abort(404, description="Resource not found")
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
