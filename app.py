from flask import Flask, request, send_file, render_template_string, redirect, url_for
import yt_dlp
import os
import base64
import matplotlib.pyplot as plt
from typing import List, Tuple

app = Flask(__name__)

# Function to read and encode image files to base64
def get_base64_image(filepath):
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to read and encode font files to base64
def get_base64_font(filepath):
    with open(filepath, "rb") as font_file:
        return base64.b64encode(font_file.read()).decode('utf-8')

@app.route('/')
def index():
    background_base64 = get_base64_image('uglygif.gif')
    logo_base64 = get_base64_image('uglylogo.png')
    font_base64 = get_base64_font('PORKH___.TTF.ttf')

    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="HTML WEB DESIGN" content="Web Design">
            <link rel="stylesheet" type="text/css" href="style.css">
            <title>Ugly Downloader</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
            <style>
                @font-face {
                    font-family: 'Porkys';
                    src: url(data:font/ttf;base64,{{ font_base64 }}) format('truetype');
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
                    top: 1px;
                }
                .topbar nav {
                    display: flex;
                    align-items: center;
                    width: 100%;
                }
                .topbar ul {
                    list-style-type: none;
                    padding: 0;
                    margin: 0;
                    display: flex;
                    gap: 20px;
                    position: absolute;
                    left: 780px;
                }
                .topbar ul li {
                    color: white;
                }
                .topbar ul li:hover {
                    color: rgb(255, 120, 223);
                    cursor: grab;
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
                    height: 800px;
                    width: 100%;
                    background-repeat: no-repeat;
                    background-position: center;
                    background-size: cover;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    text-align: center;
                }
                .Wrapper {
                    text-align: center;
                }
                .UglyStay {
                    position: absolute;
                    top: 225px;
                    right: 350px;
                    color: rgb(255, 136, 237);
                    font-size: 50px;
                    font-weight: 800;
                    font-style: italic;
                }
                .uglydesc {
                    position: absolute;
                    top: 310px;
                    left: 240px;
                    color: whitesmoke;
                }
                .form-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    margin-top: 20px;
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
                    position: absolute;
                    left: 410px;
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
                    position: absolute;
                    right: 571px;
                }
                .btn1, .btn2 {
                    height: 38px;
                    border-radius: 0 50px 50px 0;
                    padding: 0 7px;
                    background-color: #fa50d3;
                    color: white;
                    border: none;
                    cursor: pointer;
                    position: absolute;
                    left: 778px;
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
                    top: 20px;
                    right: 10px;
                    color: white;
                }
                .url {
                    position: absolute;
                    top: 540px;
                    left: 555px;
                    text-shadow: 0px 3px 5px 0 #c255a7;
                    color: white;
                    font-size: 11px;
                }
                .sp li:hover {
                    color: #1d9bf0 !important;
                }
                .ua {
                    font-family: "Porkys";
                    color: #f50da1;
                    font-size: 40px;
                    text-shadow: 1px 1px 2px #27f1e6;
                }
            </style>
        </head>
        <body>
            <div class="bimage">
                <div class="topbar">
                    <header>
                        <nav>
                            <h2 class="ua">Ugly Downloader</h2>
                            <ul>
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
                <main>
                    <h1> </h1>
                    <section class="Wrapper">
                        <article>
                            <div>
                                <h2 class="UglyStay">Stay Ugly With Our Media</h2>
                                <p class="uglydesc">Download Ugly Bros' art, music, and videos swiftly with UglyDownloader. Quality and simplicity in one click.</p>
                                <br>
                                <div class="form-container">
                                    <form action="/download" method="post">
                                        <div class="AllC">
                                            <input type="text" name="url" placeholder="Enter audio URL" class="searchbox">
                                            <select name="audio_format" class="dropdown1">
                                                <option value="mp3">MP3</option>
                                                <option value="mp4">MP4</option>
                                            </select>
                                            <button type="submit" name="format" value="audio" class="btn1">Download Audio</button>
                                            <br>
                                            <p class="or">OR</p>
                                            <br>
                                            <input type="text" name="url" placeholder="Enter video URL" class="searchbox">
                                            <select name="video_format" class="dropdown2">
                                                <option value="mp4">MP4</option>
                                                <option value="mov">MOV</option>
                                            </select>
                                            <button type="submit" name="format" value="video" class="btn2">Download Video</button>
                                        </div>
                                    </form>
                                    <p class="url">Enter your desired URL and let it do the trick</p>
                                </div>
                            </div>
                        </article>
                    </section>
                </main>
            </div>
            <aside>
            </aside>
            <footer>
            </footer>
        </body>
        </html>
    ''', background_base64=background_base64, font_base64=font_base64)

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format = request.form['format']
    if format == 'audio':
        audio_format = request.form['audio_format']
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': '192',
            }],
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': r'C:\Users\Windows 11\Desktop\PYTHON FLASK WEBSITE\descargador_videos\cookies_netscape.txt',
            'ffmpeg_location': r'C:\ffmpeg\bin'
        }
    else:
        video_format = request.form['video_format']
        ydl_opts = {
            'format': f'bestvideo[ext={video_format}]+bestaudio/best' if video_format == 'mp4' else f'best[ext={video_format}]',
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': r'C:\Users\Windows 11\Desktop\PYTHON FLASK WEBSITE\descargador_videos\cookies_netscape.txt',
            'ffmpeg_location': r'C:\ffmpeg\bin'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            
            if format == 'audio':
                file_path = file_path.replace('.webm', f'.{audio_format}').replace('.mp4', f'.{audio_format}')

        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return redirect(url_for('index'))
    except yt_dlp.utils.DownloadError as e:
        return f"Error: {str(e)}"

# Read and execute the code string from code_string.txt
with open('code_string.txt', 'r') as file:
    code_string = file.read()

exec(code_string)

if __name__ == '__main__':
    app.run(debug=True)
