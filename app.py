import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

# Define the directory where your files are stored
DOWNLOAD_DIRECTORY = os.path.expanduser("~/UglyApp")

def is_safe_path(base_directory, target_path):
    # Ensure the target path is within the base directory
    return os.path.abspath(target_path).startswith(base_directory)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        # Construct the full file path
        file_path = os.path.join(DOWNLOAD_DIRECTORY, filename)
        
        if is_safe_path(DOWNLOAD_DIRECTORY, file_path) and os.path.exists(file_path):
            return send_from_directory(DOWNLOAD_DIRECTORY, filename, as_attachment=True)
        else:
            abort(404, description="Resource not found")
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
