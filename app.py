from flask import Flask, render_template, request, jsonify
import logging
import tempfile
import os
from streamer import start_streaming, stop_streaming, check_ffmpeg
from typing import Dict, Any

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

streams: Dict[str, Dict[str, Any]] = {}
temp_dir = tempfile.mkdtemp()

@app.route('/')
def index():
    ffmpeg_installed = check_ffmpeg()
    logging.info(f"FFmpeg installed: {ffmpeg_installed}")
    return render_template('index.html', ffmpeg_installed=ffmpeg_installed)

@app.route('/start_stream', methods=['POST'])
def start_stream():
    data = request.json
    stream_id = data.get('stream_id')
    video_file = data.get('video_file')
    audio_file = data.get('audio_file')
    stream_url = data.get('stream_url')
    stream_key = data.get('stream_key')

    if not all([stream_id, video_file, audio_file, stream_url, stream_key]):
        return jsonify({"status": "error", "message": "Missing required parameters"})

    if stream_id in streams:
        return jsonify({"status": "error", "message": "Stream ID already exists"})

    try:
        stream_config = {
            'video_file': video_file,
            'audio_file': audio_file,
            'stream_url': stream_url,
            'stream_key': stream_key
        }
        process = start_streaming(stream_config)
        streams[stream_id] = {
            'process': process,
            'config': stream_config
        }
        logging.info(f"Stream {stream_id} started successfully")
        return jsonify({"status": "success", "message": f"Stream {stream_id} started"})
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

@app.route('/stop_stream', methods=['POST'])
def stop_stream():
    stream_id = request.json.get('stream_id')
    if not stream_id:
        return jsonify({"status": "error", "message": "Missing stream ID"})

    if stream_id not in streams:
        return jsonify({"status": "error", "message": "Stream not found"})

    try:
        stop_streaming(streams[stream_id]['process'])
        del streams[stream_id]
        logging.info(f"Stream {stream_id} stopped")
        return jsonify({"status": "success", "message": f"Stream {stream_id} stopped"})
    except Exception as e:
        logging.error(f"An error occurred while stopping stream {stream_id}: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

@app.route('/list_streams', methods=['GET'])
def list_streams():
    return jsonify({
        "status": "success",
        "streams": list(streams.keys())
    })

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