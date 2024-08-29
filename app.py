from flask import Flask, render_template, request, jsonify
import configparser
import os
import logging
from streamer import start_streaming, stop_streaming, check_ffmpeg

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to store the streaming process
stream_process = None


def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


@app.route('/')
def index():
    config = get_config()
    video_path = os.path.abspath(config['Paths']['video_file'])
    ffmpeg_installed = check_ffmpeg()
    logging.info(f"FFmpeg installed: {ffmpeg_installed}")
    return render_template('index.html', video_path=video_path, ffmpeg_installed=ffmpeg_installed)


@app.route('/start_stream', methods=['POST'])
def start_stream():
    global stream_process
    if stream_process and stream_process.poll() is None:
        return jsonify({"status": "error", "message": "Stream is already running"})

    try:
        stream_process = start_streaming()
        logging.info("Stream started successfully")
        return jsonify({"status": "success", "message": "Stream started"})
    except FileNotFoundError as e:
        logging.error(f"File not found error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})


@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    global stream_process
    if stream_process and stream_process.poll() is None:
        stop_streaming(stream_process)
        stream_process = None
        logging.info("Stream stopped")
        return jsonify({"status": "success", "message": "Stream stopped"})
    logging.warning("No active stream to stop")
    return jsonify({"status": "error", "message": "No active stream to stop"})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')