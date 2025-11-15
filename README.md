# YouTube Streamer

A Python-based web application for streaming video content to YouTube Live and other RTMP-compatible platforms. Features a simple web interface for managing multiple concurrent streams with independent video and audio sources.

## Features

- **Multiple Concurrent Streams**: Manage multiple live streams simultaneously with unique identifiers
- **Separate Audio/Video Sources**: Use different files for video and audio tracks
- **Loop Playback**: Automatically loop both video and audio content indefinitely
- **Web-Based Control**: Simple, intuitive web interface for stream management
- **RTMP Streaming**: Compatible with YouTube Live, Twitch, Facebook Live, and other RTMP platforms
- **Real-time Stream Management**: Start, stop, and monitor active streams in real-time
- **Automatic Port Selection**: Finds available ports automatically if default is in use

## Prerequisites

- **Python 3.7+**
- **FFmpeg**: Must be installed and accessible from command line
- **Operating System**: Linux, macOS, or Windows

### Installing FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rakeshgangwar/youtube_streamer.git
   cd youtube_streamer
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify FFmpeg installation:**
   ```bash
   ffmpeg -version
   ```

## Project Structure

```
youtube_streamer/
├── app.py                 # Flask web application and API endpoints
├── streamer.py           # FFmpeg streaming logic and process management
├── gui.py                # PyQt5 desktop GUI (legacy/optional)
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── templates/
│   └── index.html       # Web interface HTML
├── static/
│   ├── css/
│   │   └── style.css    # Web interface styles
│   └── js/
│       └── script.js    # Web interface JavaScript
└── media/               # Sample media files (video/audio)
    ├── video.mp4
    ├── audio.mp3
    └── sample.mp4
```

## Usage

### Starting the Application

1. **Run the Flask application:**
   ```bash
   python3 app.py
   ```

2. **Access the web interface:**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

   If port 5000 is in use, the application will automatically try ports 5001-5009.

### Creating a Stream

1. **Get your RTMP credentials:**
   - For YouTube Live: Go to YouTube Studio → Go Live → Stream Settings
   - Copy the **Stream URL** (e.g., `rtmp://a.rtmp.youtube.com/live2`)
   - Copy the **Stream Key** (keep this secret!)

2. **In the web interface, enter:**
   - **Stream ID**: A unique identifier for this stream (e.g., `stream1`)
   - **Video File Path**: Absolute or relative path to your video file (e.g., `media/video.mp4`)
   - **Audio File Path**: Absolute or relative path to your audio file (e.g., `media/audio.mp3`)
   - **RTMP URL**: Your streaming platform's RTMP URL
   - **Stream Key**: Your secret stream key

3. **Click "Start Stream"**

### Managing Streams

- **View Active Streams**: All active streams are listed in the "Active Streams" section
- **Stop a Stream**: Click the "Stop" button next to the stream ID
- **Multiple Streams**: Create multiple streams with different IDs and configurations

### API Endpoints

The application provides REST API endpoints for programmatic control:

#### Start a Stream
```bash
curl -X POST http://localhost:5000/start_stream \
  -H "Content-Type: application/json" \
  -d '{
    "stream_id": "stream1",
    "video_file": "media/video.mp4",
    "audio_file": "media/audio.mp3",
    "stream_url": "rtmp://a.rtmp.youtube.com/live2",
    "stream_key": "your-stream-key"
  }'
```

#### Stop a Stream
```bash
curl -X POST http://localhost:5000/stop_stream \
  -H "Content-Type: application/json" \
  -d '{"stream_id": "stream1"}'
```

#### List Active Streams
```bash
curl http://localhost:5000/list_streams
```

## Configuration

### FFmpeg Stream Settings

The application uses the following FFmpeg settings (configured in `streamer.py:46-52`):

- **Video Codec**: H.264 (libx264)
- **Preset**: veryfast (balance between speed and quality)
- **Max Bitrate**: 3000k
- **Buffer Size**: 6000k
- **Pixel Format**: yuv420p (maximum compatibility)
- **GOP Size**: 50 frames
- **Audio Codec**: AAC
- **Audio Bitrate**: 160k
- **Audio Channels**: 2 (stereo)
- **Sample Rate**: 44100 Hz

To modify these settings, edit the FFmpeg command in `streamer.py`.

### Media Files

Sample media files are provided in the `media/` directory:
- `video.mp4`: Sample video file
- `audio.mp3`: Sample audio file
- `sample.mp4`: Alternative sample video

You can use your own media files by providing the correct path when creating a stream.

## Troubleshooting

### FFmpeg Not Found
**Error**: `FFmpeg not detected`

**Solution**:
- Ensure FFmpeg is installed: `ffmpeg -version`
- Add FFmpeg to your system PATH
- Restart the application after installing FFmpeg

### File Not Found Errors
**Error**: `Audio file not found` or `Video file not found`

**Solution**:
- Verify the file paths are correct
- Use absolute paths for files outside the project directory
- Check file permissions

### Port Already in Use
**Error**: `Address already in use`

**Solution**: The application automatically tries ports 5000-5009. If all are in use:
- Stop other applications using these ports
- Modify the port range in `app.py:80-81`

### Stream Not Appearing on YouTube
**Issues**: Stream starts but doesn't appear on YouTube

**Solution**:
- Verify your Stream URL and Stream Key are correct
- Check YouTube Studio for stream status
- Ensure your YouTube channel is verified for live streaming
- Check FFmpeg output in console for errors
- Verify your video format meets YouTube requirements

### Permission Denied Errors
**Error**: Permission errors when accessing files

**Solution**:
- Check file permissions: `ls -l media/`
- Ensure the application has read access to media files
- On Linux/macOS: `chmod 644 media/*`

## Development

### Running in Debug Mode

Debug mode is enabled by default in `app.py:84`. This provides:
- Detailed error messages
- Automatic reloading on code changes
- Enhanced logging output

### Logging

The application uses Python's logging module. Logs include:
- INFO: Stream start/stop events
- DEBUG: FFmpeg commands, configuration details
- ERROR: Exceptions and failures

Check the console output for detailed logging information.

## Technical Details

### Stream Loop Mechanism

Both video and audio are looped independently using FFmpeg's `-stream_loop -1` parameter, ensuring continuous playback.

### Process Management

Each stream runs as a separate subprocess (FFmpeg process), allowing multiple independent streams with different configurations.

### Video/Audio Synchronization

The application maps video from the first input (`-map 0:v`) and audio from the second input (`-map 1:a`), allowing different loop lengths without synchronization issues.

## Known Limitations

1. **No Stream Health Monitoring**: The application doesn't monitor if a stream disconnects or fails after starting
2. **No Persistent Storage**: Stream configurations are not saved between application restarts
3. **Limited Error Recovery**: If FFmpeg crashes, the stream must be manually restarted
4. **No Authentication**: Web interface has no built-in authentication (use reverse proxy for security)

## Security Considerations

- **Never commit stream keys to version control**: Always keep them secret
- **Use HTTPS in production**: Deploy behind a reverse proxy with SSL/TLS
- **Implement authentication**: Add authentication for production deployments
- **Validate file paths**: Ensure user-provided paths don't access sensitive files
- **Rate limiting**: Consider adding rate limits to prevent abuse

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit with clear messages (`git commit -m 'Add feature: description'`)
6. Push to your fork (`git push origin feature/your-feature`)
7. Create a Pull Request

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions and classes
- Comment complex logic

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Video processing powered by [FFmpeg](https://ffmpeg.org/)
- UI enhanced with [jQuery](https://jquery.com/)

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for similar problems
- Provide detailed information (OS, Python version, error messages)

## Roadmap

Potential future enhancements:
- Stream health monitoring and auto-restart
- Persistent configuration storage
- User authentication and multi-user support
- Real-time stream statistics and metrics
- Scheduled streaming
- Cloud deployment guides (Docker, Kubernetes)
- Stream recording functionality
- Multiple quality presets
