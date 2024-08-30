from flask import Flask, render_template, request, jsonify
import configparser
import os
import logging
import tempfile
import requests
from streamer import start_streaming, stop_streaming, check_ffmpeg, get_config

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

stream_process = None
temp_dir = tempfile.mkdtemp()
video_file = None

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def download_video(url):
    global video_file
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('video/'):
            raise ValueError("The URL does not point to a video file")
        
        file_extension = content_type.split('/')[-1]
        video_file = os.path.join(temp_dir, f"downloaded_video.{file_extension}")
        
        with open(video_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return video_file
    except requests.RequestException as e:
        raise Exception(f"Failed to download video: {str(e)}")

@app.route('/')
def index():
    ffmpeg_installed = check_ffmpeg()
    logging.info(f"FFmpeg installed: {ffmpeg_installed}")
    return render_template('index.html', ffmpeg_installed=ffmpeg_installed)

@app.route('/start_stream', methods=['POST'])
def start_stream():
    global stream_process, video_file
    if stream_process and stream_process.poll() is None:
        return jsonify({"status": "error", "message": "Stream is already running"})

    url = request.json.get('url')
    if not url:
        return jsonify({"status": "error", "message": "No URL provided"})

    try:
        logging.debug("Attempting to get configuration")
        config = get_config()
        logging.debug("Configuration retrieved successfully")

        logging.debug("Attempting to download video")
        # video_file = download_video(url)
        # logging.debug(f"Video downloaded to: {video_file}")
        
        logging.debug("Attempting to start streaming")
        stream_process = start_streaming(video_file)
        logging.info("Stream started successfully")
        return jsonify({"status": "success", "message": "Stream started"})
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    global stream_process, video_file
    if stream_process and stream_process.poll() is None:
        stop_streaming(stream_process)
        stream_process = None
        if video_file and os.path.exists(video_file):
            os.remove(video_file)
            video_file = None
        logging.info("Stream stopped and temporary file removed")
        return jsonify({"status": "success", "message": "Stream stopped"})
    logging.warning("No active stream to stop")
    return jsonify({"status": "error", "message": "No active stream to stop"})

if __name__ == '__main__':
    port = 5000
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            app.run(debug=True, host='0.0.0.0', port=port)
            break
        except OSError as e:
            if "Address already in use" in str(e):
                port += 1
                print(f"Port {port-1} is in use, trying port {port}")
            else:
                raise
    else:
        print(f"Unable to find an open port after {max_attempts} attempts")