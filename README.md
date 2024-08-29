# YouTube Streamer

This is a simple Python application that allows you to stream a video file to YouTube Live using FFmpeg.

## Features

- Stream a video file to YouTube Live
- Web interface for easy control
- Uses FFmpeg for video processing and streaming

## Requirements

- Python 3.7+
- Flask
- FFmpeg

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/youtube_streamer.git
   cd youtube_streamer
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure FFmpeg is installed on your system and accessible from the command line.

## Configuration

1. Create a `config.ini` file in the project root directory with the following content:

   ```ini
   [Paths]
   video_file = path/to/your/video.mp4

   [YouTube]
   stream_url = rtmp://a.rtmp.youtube.com/live2
   stream_key = your-youtube-stream-key

   [Streaming]
   video_bitrate = 3000k
   audio_bitrate = 128k
   ```

2. Replace `path/to/your/video.mp4` with the path to your video file.
3. Replace `your-youtube-stream-key` with your actual YouTube stream key.

## Usage

1. Start the application:
   ```
   python3 app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Use the web interface to start and stop streaming.

## Notes

- The streaming key is currently stored in the `config.ini` file. Make sure to keep this file secure and do not share it publicly.
- You may need to update the streaming key in the `config.ini` file for each new YouTube Live event.

## Troubleshooting

- If you encounter issues with FFmpeg not being detected, ensure it's properly installed and added to your system's PATH.
- Check the console output for any error messages if streaming fails to start.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.