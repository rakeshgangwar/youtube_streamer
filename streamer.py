import logging
import os
import subprocess
import shlex
import configparser
from typing import Dict, Any

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_config():
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

def start_streaming(stream_config: Dict[str, Any]):
    video_file = stream_config['video_file']
    audio_file = stream_config['audio_file']
    stream_url = stream_config['stream_url']
    stream_key = stream_config['stream_key']

    if not os.path.exists(audio_file):
        logging.error(f"Audio file not found: {audio_file}")
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    if not os.path.exists(video_file):
        logging.error(f"Video file not found: {video_file}")
        raise FileNotFoundError(f"Video file not found: {video_file}")

    command = (
        f"ffmpeg -stream_loop -1 -re -i {video_file} "
        f"-stream_loop -1 -i {audio_file} "
        f"-c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k "
        f"-pix_fmt yuv420p -g 50 -c:a aac -b:a 160k -ac 2 -ar 44100 "
        f"-map 0:v -map 1:a "
        f"-f flv {stream_url}/{stream_key}"
    )
    
    logging.debug(f"Executing command: {command}")
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def stop_streaming(process):
    if process:
        process.terminate()
        process.wait()

def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config