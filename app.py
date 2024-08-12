from flask import Flask, render_template_string, jsonify
from flask_socketio import SocketIO, emit
import gevent
import gevent.monkey
import logging
import traceback

# Patch the standard library to make it cooperative with gevent
gevent.monkey.patch_all()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SocketIO Test</title>
        <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
        <script type="text/javascript">
            localStorage.debug = 'socket.io-client:*'; // Enable debug logs in the browser
            document.addEventListener('DOMContentLoaded', function() {
                var socket = io();

                socket.on('connect', function() {
                    console.log('Connected to server');
                    document.getElementById('status').innerHTML = 'Connected to server';
                });

                socket.on('test_response', function(data) {
                    console.log('Response from server:', data);
                    document.getElementById('response').innerHTML = 'Response from server: ' + data.message;
                });

                document.getElementById('sendButton').addEventListener('click', function() {
                    console.log('Sending test message to server');
                    socket.emit('test_message', {'data': 'Hello from client'});
                });

                socket.on('disconnect', function() {
                    console.error('Disconnected from server');
                    document.getElementById('status').innerHTML = 'Disconnected from server';
                });

                socket.on('connect_error', function(error) {
                    console.error('Connection error:', error);
                    document.getElementById('status').innerHTML = 'Connection error: ' + error;
                });

                socket.on('connect_timeout', function() {
                    console.error('Connection timed out');
                    document.getElementById('status').innerHTML = 'Connection timed out';
                });

                socket.on('reconnect_attempt', function() {
                    console.log('Attempting to reconnect...');
                    document.getElementById('status').innerHTML = 'Attempting to reconnect...';
                });

                socket.on('reconnect_failed', function() {
                    console.error('Reconnection failed');
                    document.getElementById('status').innerHTML = 'Reconnection failed';
                });
            });
        </script>
    </head>
    <body>
        <h1>Socket.IO Test</h1>
        <p id="status">Not connected</p>
        <button id="sendButton">Send Test Message</button>
        <p id="response">No response yet</p>
    </body>
    </html>
    ''')

@socketio.on('test_message')
def handle_test_message(json):
    try:
        logger.debug(f'Received test message: {json}')
        emit('test_response', {'message': 'Hello from server'})
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}", exc_info=True)

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error("Unhandled exception", exc_info=True)
    response = {
        "message": "An internal error occurred.",
        "details": str(e)
    }
    return jsonify(response), 500

if __name__ == '__main__':
    try:
        socketio.run(app, host='0.0.0.0', port=8000, debug=True)
    except Exception as e:
        logger.error(f"Critical error on startup: {str(e)}", exc_info=True)
