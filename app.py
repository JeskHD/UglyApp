import os
import subprocess
from flask import Flask, render_template_string, request, redirect, flash, send_file
import tweepy
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Twitter API credentials
api_key = os.getenv('TWITTER_API_KEY')
api_secret_key = os.getenv('TWITTER_API_SECRET_KEY')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
cookie_file = os.getenv('TWITTER_COOKIE_FILE')

# Print the environment variables to verify they are loaded correctly
print(f"API Key: {api_key}")
print(f"API Secret Key: {api_secret_key}")
print(f"Access Token: {access_token}")
print(f"Access Token Secret: {access_token_secret}")
print(f"Cookie File: {cookie_file}")

# Authenticate to Twitter
auth = tweepy.OAuth1UserHandler(api_key, api_secret_key, access_token, access_token_secret)
api = tweepy.API(auth)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="HTML WEB DESIGN" content="Web Design">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ugly Downloader</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <style>
        @font-face {
            font-family: 'Porkys';
            format('woff');
            font-weight: normal;
            font-style: normal;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: "Poppins", sans-serif;
            width: 100%;
            overflow-x: hidden;
        }
        .topbar {
            font-family: "Montserrat", "Poppins", "Avenir";
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 50px;
            background: rgba(0, 0, 0, 0.5);
            position: absolute;
            top: 0;
            z-index: 1000;
        }
        .topbar nav {
            display: flex;
            align-items: center;
            width: 100%;
        }
        .topbar .menu-toggle {
            display: none;
            font-size: 24px;
            color: white;
            cursor: pointer;
            position: absolute;
            right: 40px;
        }
        .topbar ul {
            list-style-type: none;
            padding: 0;
            margin: 0;
            display: flex;
            gap: 20px;
            position: absolute;
            right: 50px;
        }
        .topbar ul li {
            color: white;
        }
        .topbar ul li:hover {
            color: rgb(255, 120, 223);
            cursor: pointer;
        }
        .poppins-medium-italic {
            font-family: "Poppins", sans-serif;
            font-weight: 500;
            font-style: italic;
        }
        .topbar img {
            height: 65px;
            width: auto;
            position: relative;
            top: 2px;
        }
        .bimage {
            background: linear-gradient(rgba(255, 7, 156, 0.585), rgba(104, 97, 97, 0.5)), url("data:image/gif;base64,{{ background_base64 }}");
            min-height: 100vh;
            width: 100%;
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding-top: 100px; /* Adjusted to move content closer to the topbar */
        }
        .Wrapper {
            text-align: center;
            padding: 20px;
            width: 100%;
            max-width: 1200px;
        }
        .UglyStay {
            color: rgb(255, 136, 237);
            font-size: 50px;
            font-weight: 800;
            font-style: italic;
            margin: 0 20px;
            text-align: center;
            width: 100%;
        }
        .uglydesc {
            color: whitesmoke;
            margin: 20px 10px;
            font-size: 18px;
            text-align: center;
            width: 100%;
        }
        .form-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        .searchbox {
            width: 300px;
            height: 40px;
            background-color: black;
            border-radius: 50px 0 0 50px;
            color: white;
            font-family: "Poppins", sans-serif;
            text-align: center;
            border: none;
            padding-left: 20px;
        }
        .searchbox:hover {
            border: 1px solid #ff78df;
        }
        .dropdown1, .dropdown2 {
            height: 38px;
            border-radius: 0;
            padding: 0 9px;
            border: none;
            font-family: "Poppins", sans-serif;
            background-color: #ff78df;
            color: white;
        }
        .btn1, .btn2 {
            height: 38px;
            border-radius: 0 50px 50px 0;
            padding: 0 7px;
            background-color: #fa50d3;
            color: white;
            border: none;
            cursor: pointer;
            font-family: "Poppins", sans-serif;
        }
        .btn1:active, .btn2:active {
            color: #fb85df;
            background-color: #f8a1e4;
        }
        .btn1:hover, .btn2:hover {
            background-color: #e767c7;
        }
        .or {
            position: relative;
            top: 15px;
            color: white;
            font-size: 18px;
            margin: 10px 0;
        }
        .url {
            text-shadow: 0px 3px 5px 0 #c255a7;
            color: white;
            font-size: 14px;
            margin-top: 10px;
            width: 100%;
            text-align: center;
        }
        .sp li:hover {
            color: #1d9bf0 !important;
        }
        .ua {
            font-family: 'Porkys';
            color: #f50da1;
            font-size: 40px;
            text-shadow: 1px 1px 2px #27f1e6;
        }
        .flashes {
            color: red;
            list-style: none;
            text-align: center;
            margin-top: 10px;
        }
        /* Responsive Design */
        @media (max-width: 800px) {
            .topbar {
                flex-direction: row;
                align-items: center;
                padding: 10px 10px;
            }
            .topbar .menu-toggle {
                display: block;
            }
            .topbar ul {
                display: none;
                flex-direction: column;
                align-items: center;
                width: 100%;
                margin-top: 10px;
            }
            .topbar ul.active {
                display: flex;
                font-size: 10px;
                top: 11px;
                border: 1px solid white;
                flex-direction: column;
                position: absolute;
                background-color: rgba(0, 0, 0, 0.8);
                right: 10px;
                top: 30px;
                width: 200px;
                padding: 10px;
            }
            .topbar h2 {
                font-size: 24px;
            }
            .UglyStay {
                font-size: 30px;
                margin-top: 40px;
                text-align: center;
                position: relative;
                right: 16px;
            }
            .uglydesc {
                font-size: 16px;
                margin: 20px 20px;
                text-align: center;
                position: relative;
                right: 16px;
            }
            .form-container {
                flex-direction: column;
                align-items: center;
            }
            .searchbox, .dropdown1, .dropdown2, .btn1, .btn2 {
                width: 100%;
                margin-bottom: 10px;
            }
            .or {
                top: 0;
                margin: 10px 0;
            }
            .url {
                margin-top: 20px;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="topbar">
        <header>
            <nav>
                <h2 class="ua">Ugly Downloader</h2>
                <div class="menu-toggle">
                    <i class="fa fa-bars"></i>
                </div>
                <ul class="menu">
                    <li>About Us</li>
                    <li>Collection</li>
                    <li>Media</li>
                    <li>FAQ</li>
                    <li>Downloader</li>
                    <div class="sp">
                        <li><i class="fa fa-twitter"></i></li>
                    </div>
                </ul>
            </nav>
        </header>
    </div>
    <div class="bimage">
        <main>
            <h1></h1>
            <section class="Wrapper">
                <article>
                    <div>
                        <h2 class="UglyStay">Stay Ugly With Our Media</h2>
                        <p class="uglydesc">Download Ugly Bros' art, music, and videos swiftly with UglyDownloader. Quality and simplicity in one click.</p>
                        <br>
                        <div class="form-container">
                            <form action="/download" method="post" enctype="multipart/form-data">
                                <div class="AllC">
                                    <input type="text" name="audio_url" placeholder="Enter audio URL" class="searchbox">
                                    <select name="audio_format" class="dropdown1">
                                        <option value="mp3">MP3</option>
                                        <option value="m4a">M4A</option>
                                    </select>
                                    <button type="submit" name="format" value="audio" class="btn1">Download Audio</button>
                                    <br>
                                    <p class="or">OR</p><br>
                                    <input type="text" name="video_url" placeholder="Enter video URL" class="searchbox">
                                    <select name="video_format" class="dropdown2">
                                        <option value="mp4">MP4</option>
                                        <option value="mov">MOV</option>
                                    </select>
                                    <button type="submit" name="format" value="video" class="btn2">Download Video</button>
                                    <br><br>
                            </form>
                            <p class="url">Enter your desired URL and let it do the trick</p>
                            <div class="message">
                                {% with messages = get_flashed_messages() %}
                                    {% if messages %}
                                        <ul class="flashes">
                                        {% for message in messages %}
                                            <li>{{ message }}</li>
                                        {% endfor %}
                                        </ul>
                                    {% endif %}
                                {% endwith %}
                            </div>
                        </div>
                    </div>
                </article>
            </section>
        </main>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, background_base64='')

@app.route('/download', methods=['POST'])
def download():
    audio_url = request.form.get('audio_url')
    audio_format = request.form.get('audio_format')
    video_url = request.form.get('video_url')
    video_format = request.form.get('video_format')

    if audio_url:
        file_name = f"downloaded_audio.{audio_format}"
        if download_twspace(audio_url, file_name):
            return send_file(file_name, as_attachment=True)

    if video_url:
        file_name = f"downloaded_video.{video_format}"
        if download_video(video_url, file_name):
            return send_file(file_name, as_attachment=True)

    flash('Please provide a valid URL')
    return redirect('/')

def download_twspace(url, file_name):
    if not cookie_file or cookie_file == 'None':
        flash('Cookie file is not set. Please check your .env configuration.')
        return False
    try:
        command = f"twspace_dl -c {cookie_file} -i {url} -o {file_name}"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and os.path.exists(file_name):
            return True
        else:
            flash('Failed to download the Twitter Space.')
            return False
    except Exception as e:
        flash(f'Failed to download the Twitter Space: {e}')
        return False

def download_video(url, file_name):
    ydl_opts = {
        'format': 'best',
        'outtmpl': file_name,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        flash(f'Failed to download the video: {e}')
        return False

if __name__ == '__main__':
    app.run(debug=True)
