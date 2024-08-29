import subprocess
import configparser
import os
import shutil


def get_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


def start_streaming():
    config = get_config()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(base_dir, config['Paths']['video_file'])

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        raise FileNotFoundError("FFmpeg not found. Please make sure FFmpeg is installed.")

    command = [
        ffmpeg_path,
        '-re', '-i', video_path,
        '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', config['Streaming']['video_bitrate'],
        '-maxrate', config['Streaming']['video_bitrate'], '-bufsize', '6000k',
        '-pix_fmt', 'yuv420p', '-g', '50', '-c:a', 'aac', '-b:a', config['Streaming']['audio_bitrate'],
        '-ar', '44100', '-f', 'flv',
        f"{config['YouTube']['stream_url']}/{config['YouTube']['stream_key']}"
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception as e:
        raise Exception(f"An error occurred while starting FFmpeg: {str(e)}")

    return process


def stop_streaming(process):
    if process:
        process.terminate()
        process.wait()


def check_ffmpeg():
    try:
        # Try to find ffmpeg in PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            print(f"FFmpeg found at: {ffmpeg_path}")
        else:
            print("FFmpeg not found in PATH")

        # Try to run ffmpeg -version
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        print("FFmpeg version information:")
        print(result.stdout.split('\n')[0])  # Print just the first line of version info
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e}")
        return False
    except FileNotFoundError:
        print("FFmpeg executable not found")
        return False
    except Exception as e:
        print(f"Unexpected error checking FFmpeg: {e}")
        return False


if __name__ == "__main__":
    if not check_ffmpeg():
        print("FFmpeg is not installed or not in your system PATH.")
        print("Please install FFmpeg using: sudo apt install ffmpeg")
    else:
        print("FFmpeg is installed and accessible.")