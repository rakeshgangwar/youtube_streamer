"""
YouTube Streamer Flask Application

This module provides a web-based interface for managing multiple concurrent
video streams to RTMP platforms like YouTube Live, Twitch, and Facebook Live.

The application uses FFmpeg for video processing and provides REST API endpoints
for stream management.
"""

from flask import Flask, render_template, request, jsonify
import logging
import tempfile
import os
from streamer import start_streaming, stop_streaming, check_ffmpeg
from typing import Dict, Any

app = Flask(__name__)

# Configure logging with timestamp, level, and message
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Global dictionary to store active streams
# Key: stream_id (str), Value: dict with 'process' and 'config'
streams: Dict[str, Dict[str, Any]] = {}

# Create temporary directory for potential file operations
temp_dir = tempfile.mkdtemp()

@app.route('/')
def index():
    """
    Render the main web interface.

    Checks if FFmpeg is installed and passes this information to the template
    for display to the user.

    Returns:
        str: Rendered HTML template
    """
    ffmpeg_installed = check_ffmpeg()
    logging.info(f"FFmpeg installed: {ffmpeg_installed}")
    return render_template('index.html', ffmpeg_installed=ffmpeg_installed)

@app.route('/start_stream', methods=['POST'])
def start_stream():
    """
    Start a new streaming session.

    Creates a new FFmpeg process to stream video content to an RTMP destination.
    Each stream requires a unique ID and separate video/audio file paths.

    Request JSON Parameters:
        stream_id (str): Unique identifier for this stream
        video_file (str): Path to the video file to stream
        audio_file (str): Path to the audio file to stream
        stream_url (str): RTMP server URL (e.g., rtmp://a.rtmp.youtube.com/live2)
        stream_key (str): Secret stream key from the streaming platform

    Returns:
        JSON response with status and message:
        - Success: {"status": "success", "message": "Stream {id} started"}
        - Error: {"status": "error", "message": "error description"}

    Raises:
        FileNotFoundError: If video or audio file doesn't exist
        Exception: For other streaming errors
    """
    data = request.json
    stream_id = data.get('stream_id')
    video_file = data.get('video_file')
    audio_file = data.get('audio_file')
    stream_url = data.get('stream_url')
    stream_key = data.get('stream_key')

    # Validate all required parameters are provided
    if not all([stream_id, video_file, audio_file, stream_url, stream_key]):
        return jsonify({"status": "error", "message": "Missing required parameters"})

    # Ensure stream ID is unique
    if stream_id in streams:
        return jsonify({"status": "error", "message": "Stream ID already exists"})

    try:
        # Build stream configuration
        stream_config = {
            'video_file': video_file,
            'audio_file': audio_file,
            'stream_url': stream_url,
            'stream_key': stream_key
        }

        # Start FFmpeg streaming process
        process = start_streaming(stream_config)

        # Store stream information for management
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
    """
    Stop an active streaming session.

    Terminates the FFmpeg process associated with the given stream ID and
    removes it from the active streams dictionary.

    Request JSON Parameters:
        stream_id (str): ID of the stream to stop

    Returns:
        JSON response with status and message:
        - Success: {"status": "success", "message": "Stream {id} stopped"}
        - Error: {"status": "error", "message": "error description"}
    """
    stream_id = request.json.get('stream_id')

    # Validate stream_id parameter
    if not stream_id:
        return jsonify({"status": "error", "message": "Missing stream ID"})

    # Check if stream exists
    if stream_id not in streams:
        return jsonify({"status": "error", "message": "Stream not found"})

    try:
        # Terminate the FFmpeg process
        stop_streaming(streams[stream_id]['process'])

        # Remove stream from active streams
        del streams[stream_id]
        logging.info(f"Stream {stream_id} stopped")
        return jsonify({"status": "success", "message": f"Stream {stream_id} stopped"})
    except Exception as e:
        logging.error(f"An error occurred while stopping stream {stream_id}: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"})

@app.route('/list_streams', methods=['GET'])
def list_streams():
    """
    List all currently active streams.

    Returns:
        JSON response containing:
        - status: "success"
        - streams: List of active stream IDs

    Example Response:
        {"status": "success", "streams": ["stream1", "stream2"]}
    """
    return jsonify({
        "status": "success",
        "streams": list(streams.keys())
    })

if __name__ == '__main__':
    """
    Application entry point.

    Attempts to start the Flask server on port 5000. If the port is already
    in use, automatically tries subsequent ports (5001-5009) until an available
    port is found or max_attempts is reached.
    """
    port = 5000
    max_attempts = 10

    for attempt in range(max_attempts):
        try:
            # Start Flask development server
            # debug=True enables auto-reload and detailed error pages
            # host='0.0.0.0' makes server accessible from other machines
            app.run(debug=True, host='0.0.0.0', port=port)
            break
        except OSError as e:
            if "Address already in use" in str(e):
                port += 1
                print(f"Port {port-1} is in use, trying port {port}")
            else:
                # Re-raise if it's a different OS error
                raise
    else:
        # This runs if the for loop completes without breaking
        print(f"Unable to find an open port after {max_attempts} attempts")