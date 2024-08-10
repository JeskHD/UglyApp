from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'test_secret_key'
socketio = SocketIO(app)

@app.route('/')
def index():
    # A simple template with a button to test WebSocket communication
    html_content = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SocketIO Test</title>
        <script src="https://cdn.socket.io/4.0.1/socket.io.min.js"></script>
        <script type="text/javascript">
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
    '''
    return render_template_string(html_content)

@socketio.on('test_message')
def handle_test_message(json):
    print(f'Received test message: {json}')
    emit('test_response', {'message': 'Hello from server'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
