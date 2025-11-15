"""
FFmpeg Streaming Module

This module handles the low-level FFmpeg process management for streaming
video and audio content to RTMP destinations. It provides functions for
checking FFmpeg availability, starting streams, and stopping streams.
"""

import logging
import os
import subprocess
import shlex
import configparser
from typing import Dict, Any


def check_ffmpeg() -> bool:
    """
    Check if FFmpeg is installed and accessible.

    Attempts to run 'ffmpeg -version' to verify FFmpeg is available
    in the system PATH.

    Returns:
        bool: True if FFmpeg is available, False otherwise
    """
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_config() -> configparser.ConfigParser:
    """
    Load configuration from config.ini file.

    NOTE: This function is currently unused in the application as stream
    configuration is passed directly via API parameters.

    Reads the config.ini file from the current working directory and
    validates that it contains a 'Stream' section.

    Returns:
        configparser.ConfigParser: Parsed configuration object

    Raises:
        FileNotFoundError: If config.ini doesn't exist
        KeyError: If 'Stream' section is missing from config file
    """
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    current_dir = os.getcwd()
    full_path = os.path.join(current_dir, config_file)

    logging.debug(f"Current working directory: {current_dir}")
    logging.debug(f"Looking for config file at: {full_path}")

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Configuration file '{full_path}' not found.")

    config.read(full_path)
    logging.debug(f"Sections in config: {config.sections()}")
    logging.debug(f"Full config content: {dict(config)}")

    if 'Stream' not in config:
        raise KeyError("'Stream' section not found in the configuration file.")

    logging.debug(f"Stream section: {dict(config['Stream'])}")
    return config

def start_streaming(stream_config: Dict[str, Any]) -> subprocess.Popen:
    """
    Start an FFmpeg streaming process.

    Creates and launches an FFmpeg subprocess that streams video and audio
    to an RTMP destination with looping playback.

    FFmpeg Configuration:
        - Video: H.264 codec, veryfast preset, 3000k max bitrate
        - Audio: AAC codec, 160k bitrate, stereo, 44.1kHz
        - Both video and audio loop indefinitely (-stream_loop -1)
        - Video is read at native frame rate (-re)
        - Output format: FLV for RTMP streaming

    Args:
        stream_config (dict): Configuration dictionary containing:
            - video_file (str): Path to video file
            - audio_file (str): Path to audio file
            - stream_url (str): RTMP server URL
            - stream_key (str): Stream key for authentication

    Returns:
        subprocess.Popen: The FFmpeg process object

    Raises:
        FileNotFoundError: If video or audio file doesn't exist
    """
    video_file = stream_config['video_file']
    audio_file = stream_config['audio_file']
    stream_url = stream_config['stream_url']
    stream_key = stream_config['stream_key']

    # Validate audio file exists
    if not os.path.exists(audio_file):
        logging.error(f"Audio file not found: {audio_file}")
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # Validate video file exists
    if not os.path.exists(video_file):
        logging.error(f"Video file not found: {video_file}")
        raise FileNotFoundError(f"Video file not found: {video_file}")

    # Build FFmpeg command
    # -stream_loop -1: Loop input indefinitely
    # -re: Read input at native frame rate
    # -c:v libx264: Use H.264 video codec
    # -preset veryfast: Balance encoding speed and quality
    # -maxrate 3000k: Maximum video bitrate
    # -bufsize 6000k: Rate control buffer size
    # -pix_fmt yuv420p: Pixel format for maximum compatibility
    # -g 50: GOP size (keyframe interval)
    # -c:a aac: Use AAC audio codec
    # -b:a 160k: Audio bitrate
    # -ac 2: 2 audio channels (stereo)
    # -ar 44100: Audio sample rate
    # -map 0:v: Map video from first input
    # -map 1:a: Map audio from second input
    # -f flv: Output format for RTMP
    command = (
        f"ffmpeg -stream_loop -1 -re -i {video_file} "
        f"-stream_loop -1 -i {audio_file} "
        f"-c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k "
        f"-pix_fmt yuv420p -g 50 -c:a aac -b:a 160k -ac 2 -ar 44100 "
        f"-map 0:v -map 1:a "
        f"-f flv {stream_url}/{stream_key}"
    )

    logging.debug(f"Executing command: {command}")

    # Start FFmpeg process with stdout/stderr pipes for logging
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def stop_streaming(process: subprocess.Popen) -> None:
    """
    Stop a running FFmpeg streaming process.

    Sends a termination signal to the FFmpeg process and waits for it
    to exit gracefully.

    Args:
        process (subprocess.Popen): The FFmpeg process to terminate
    """
    if process:
        process.terminate()  # Send SIGTERM signal
        process.wait()       # Wait for process to terminate


# NOTE: Duplicate function - this appears to be legacy code
# The first get_config() function (lines 18-39) is more complete
# This simpler version is kept for backward compatibility but is unused
def get_config() -> configparser.ConfigParser:
    """
    Load configuration from config.ini (simplified version).

    NOTE: This is a duplicate function. The version at line 18 is more
    complete with validation and logging. This version is kept for
    backward compatibility but is not currently used.

    Returns:
        configparser.ConfigParser: Parsed configuration object
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config