# Development Guide

This guide covers local development setup, common development tasks, testing, and troubleshooting for the YouTube Streamer project.

## Table of Contents
1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Common Development Tasks](#common-development-tasks)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Code Style and Standards](#code-style-and-standards)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)

## Development Environment Setup

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.7 or higher**
  ```bash
  python3 --version
  ```

- **pip** (Python package manager)
  ```bash
  pip3 --version
  ```

- **FFmpeg**
  ```bash
  ffmpeg -version
  ```

- **Git** (for version control)
  ```bash
  git --version
  ```

### Initial Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rakeshgangwar/youtube_streamer.git
   cd youtube_streamer
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   # Create virtual environment
   python3 -m venv venv

   # Activate virtual environment
   # On Linux/macOS:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   python3 -c "import flask; print(f'Flask version: {flask.__version__}')"
   ```

### Development Dependencies

For development, you may want to install additional packages:

```bash
# Code formatting
pip install black

# Linting
pip install pylint flake8

# Type checking
pip install mypy

# Testing (when tests are added)
pip install pytest pytest-flask
```

Create a `requirements-dev.txt` file:
```text
black==23.3.0
pylint==2.17.4
flake8==6.0.0
mypy==1.3.0
pytest==7.3.1
pytest-flask==1.2.0
```

Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

## Project Structure

```
youtube_streamer/
├── app.py                    # Main Flask application
├── streamer.py              # FFmpeg streaming logic
├── gui.py                   # PyQt5 GUI (legacy)
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies (optional)
├── README.md               # Project overview
├── .gitignore              # Git ignore rules
│
├── templates/              # HTML templates
│   └── index.html         # Main web interface
│
├── static/                # Static assets
│   ├── css/
│   │   └── style.css     # Stylesheet
│   └── js/
│       └── script.js     # JavaScript (legacy)
│
├── media/                 # Sample media files
│   ├── video.mp4
│   ├── audio.mp3
│   └── sample.mp4
│
└── docs/                  # Documentation
    ├── ARCHITECTURE.md    # Architecture documentation
    └── DEVELOPMENT.md     # This file
```

## Development Workflow

### Running the Application

1. **Start the development server**:
   ```bash
   python3 app.py
   ```

2. **Access the application**:
   - Open browser: `http://localhost:5000`
   - If port 5000 is busy, the app will try ports 5001-5009

3. **Debug mode features**:
   - Auto-reload on code changes
   - Detailed error pages
   - Interactive debugger in browser

### Making Code Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Edit the relevant files
   - Test your changes locally
   - Follow code style guidelines

3. **Test the changes**:
   ```bash
   # Run the application
   python3 app.py

   # Test in browser or with curl
   curl -X GET http://localhost:5000/list_streams
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

5. **Push to remote**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Common Development Tasks

### Adding a New API Endpoint

1. **Define the route in `app.py`**:
   ```python
   @app.route('/your_endpoint', methods=['GET', 'POST'])
   def your_endpoint():
       """
       Docstring describing the endpoint.
       """
       # Your logic here
       return jsonify({"status": "success", "data": ...})
   ```

2. **Add client-side code** in `templates/index.html`:
   ```javascript
   function callYourEndpoint() {
       fetch('/your_endpoint', {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({...})
       })
       .then(response => response.json())
       .then(data => console.log(data));
   }
   ```

3. **Test the endpoint**:
   ```bash
   curl -X POST http://localhost:5000/your_endpoint \
     -H "Content-Type: application/json" \
     -d '{"key": "value"}'
   ```

### Modifying FFmpeg Settings

FFmpeg configuration is in `streamer.py:120-126`. To modify:

1. **Locate the command string**:
   ```python
   command = (
       f"ffmpeg -stream_loop -1 -re -i {video_file} "
       f"-stream_loop -1 -i {audio_file} "
       f"-c:v libx264 -preset veryfast -maxrate 3000k -bufsize 6000k "
       # ... rest of command
   )
   ```

2. **Modify parameters**:
   ```python
   # Example: Change video bitrate
   f"-maxrate 5000k -bufsize 10000k "

   # Example: Change encoding preset
   f"-preset faster "

   # Example: Add audio filters
   f"-af \"volume=2.0\" "
   ```

3. **Test changes**:
   - Start a stream
   - Monitor FFmpeg output in console
   - Verify stream quality on platform

### Adding Environment Variable Support

1. **Create a `.env` file**:
   ```bash
   FLASK_ENV=development
   FLASK_DEBUG=True
   SECRET_KEY=your-secret-key
   MAX_STREAMS=10
   ```

2. **Install python-dotenv**:
   ```bash
   pip install python-dotenv
   ```

3. **Load environment variables in `app.py`**:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()

   MAX_STREAMS = int(os.getenv('MAX_STREAMS', 10))
   SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
   ```

4. **Add `.env` to `.gitignore`**:
   ```bash
   echo ".env" >> .gitignore
   ```

### Creating a Configuration Template

Create `config.ini.example`:
```ini
[Stream]
default_video_bitrate = 3000k
default_audio_bitrate = 160k
max_concurrent_streams = 10

[Server]
host = 0.0.0.0
port = 5000
debug = true
```

Users can copy this to `config.ini` and customize.

## Testing

### Manual Testing

1. **Test stream start**:
   ```bash
   curl -X POST http://localhost:5000/start_stream \
     -H "Content-Type: application/json" \
     -d '{
       "stream_id": "test1",
       "video_file": "media/video.mp4",
       "audio_file": "media/audio.mp3",
       "stream_url": "rtmp://your-server",
       "stream_key": "your-key"
     }'
   ```

2. **Test list streams**:
   ```bash
   curl http://localhost:5000/list_streams
   ```

3. **Test stream stop**:
   ```bash
   curl -X POST http://localhost:5000/stop_stream \
     -H "Content-Type: application/json" \
     -d '{"stream_id": "test1"}'
   ```

### Unit Testing (Future Implementation)

Create `tests/test_app.py`:
```python
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Test that index page loads."""
    rv = client.get('/')
    assert rv.status_code == 200

def test_list_streams_empty(client):
    """Test listing streams when none active."""
    rv = client.get('/list_streams')
    data = rv.get_json()
    assert data['status'] == 'success'
    assert data['streams'] == []

def test_start_stream_missing_params(client):
    """Test starting stream with missing parameters."""
    rv = client.post('/start_stream',
                     json={'stream_id': 'test'})
    data = rv.get_json()
    assert data['status'] == 'error'
```

Run tests:
```bash
pytest tests/ -v
```

### Integration Testing

Test with actual RTMP server:

1. **Set up local RTMP server** (using nginx-rtmp):
   ```bash
   # Install nginx with RTMP module
   # Configure nginx.conf with RTMP settings
   # Start nginx
   ```

2. **Stream to local server**:
   ```bash
   # Use rtmp://localhost:1935/live as stream_url
   ```

3. **Verify stream** with VLC or ffplay:
   ```bash
   ffplay rtmp://localhost:1935/live/your-stream-key
   ```

## Debugging

### Enable Debug Logging

In `app.py`, logging is already configured:
```python
logging.basicConfig(level=logging.DEBUG, ...)
```

To add more logging:
```python
import logging
logging.debug("Debug message")
logging.info("Info message")
logging.error("Error message")
```

### Debug FFmpeg Issues

1. **Check FFmpeg stderr**:
   ```python
   # In streamer.py, after starting process
   stdout, stderr = process.communicate()
   logging.error(f"FFmpeg stderr: {stderr.decode()}")
   ```

2. **Test FFmpeg command manually**:
   ```bash
   # Copy command from logs and run in terminal
   ffmpeg -stream_loop -1 -re -i media/video.mp4 \
          -stream_loop -1 -i media/audio.mp3 \
          -c:v libx264 -preset veryfast \
          # ... rest of command
   ```

3. **Monitor FFmpeg process**:
   ```bash
   # In another terminal
   ps aux | grep ffmpeg
   top -p <ffmpeg-pid>
   ```

### Using Python Debugger

Add breakpoints:
```python
import pdb; pdb.set_trace()  # Execution stops here
```

Or use IDE debuggers (VS Code, PyCharm).

### Browser Developer Tools

1. **Open DevTools** (F12)
2. **Check Console** for JavaScript errors
3. **Monitor Network** tab for API requests
4. **Inspect Elements** for UI issues

## Code Style and Standards

### Python Code Style (PEP 8)

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Max 100 characters
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

### Format Code with Black

```bash
# Format all Python files
black .

# Check without modifying
black --check .
```

### Linting with Pylint

```bash
# Lint specific file
pylint app.py

# Lint all Python files
pylint *.py
```

### Type Hints

Use type hints for better code documentation:
```python
from typing import Dict, Any, List

def start_streaming(stream_config: Dict[str, Any]) -> subprocess.Popen:
    ...

def list_streams() -> List[str]:
    ...
```

### Docstring Convention (Google Style)

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.

    Longer description if needed. Explain what the function does,
    not how it does it.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is invalid
        FileNotFoundError: When file not found
    """
    pass
```

## Troubleshooting

### Port Already in Use

**Problem**: Error starting server on port 5000

**Solution**: The app automatically tries ports 5000-5009. If all are busy:
```bash
# Find process using port
lsof -i :5000
# or on Linux
netstat -tlnp | grep 5000

# Kill the process
kill <PID>
```

### FFmpeg Not Found

**Problem**: "FFmpeg not detected" error

**Solution**:
```bash
# Verify FFmpeg installation
which ffmpeg

# Install if missing (Ubuntu/Debian)
sudo apt install ffmpeg

# Add to PATH if installed but not found
export PATH=$PATH:/path/to/ffmpeg/bin
```

### File Permission Errors

**Problem**: Cannot read video/audio files

**Solution**:
```bash
# Check file permissions
ls -l media/

# Fix permissions
chmod 644 media/*.mp4 media/*.mp3

# Check if file exists
test -f media/video.mp4 && echo "exists" || echo "not found"
```

### Virtual Environment Issues

**Problem**: Module not found after installing

**Solution**:
```bash
# Ensure virtual environment is activated
which python3  # Should show path in venv/

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

### Stream Not Appearing on Platform

**Problem**: Stream starts but doesn't appear on YouTube/Twitch

**Checklist**:
1. Verify stream URL and key are correct
2. Check platform requires stream to be scheduled
3. Verify account is enabled for live streaming
4. Check FFmpeg output for errors
5. Test with different video file
6. Verify network firewall allows RTMP (port 1935)

### High CPU Usage

**Problem**: FFmpeg consuming too much CPU

**Solutions**:
```python
# Use faster preset (lower quality, less CPU)
-preset ultrafast

# Use hardware encoding (if available)
-c:v h264_nvenc  # NVIDIA GPU
-c:v h264_qsv    # Intel QuickSync
-c:v h264_videotoolbox  # macOS

# Reduce resolution
-vf scale=1280:720  # 720p instead of 1080p

# Reduce framerate
-r 24  # 24fps instead of 30fps
```

## Contributing

### Setting Up for Contribution

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/youtube_streamer.git
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/rakeshgangwar/youtube_streamer.git
   ```
4. Create feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```

### Pull Request Process

1. **Update from upstream**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes**:
   - Write clean, documented code
   - Add tests if applicable
   - Update documentation

3. **Test thoroughly**:
   - Run the application
   - Test all affected features
   - Check for regressions

4. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: clear description

   - Bullet point of what changed
   - Another bullet point
   - Fixes #issue-number"
   ```

5. **Push and create PR**:
   ```bash
   git push origin feature/your-feature
   ```
   Then create Pull Request on GitHub.

### Code Review Checklist

Before submitting PR, verify:
- [ ] Code follows PEP 8 style
- [ ] All functions have docstrings
- [ ] No debugging code (print statements, pdb)
- [ ] Updated documentation if needed
- [ ] Tested manually
- [ ] No secrets/keys committed
- [ ] Added type hints where applicable

## Development Best Practices

### Version Control

- **Commit frequently** with clear messages
- **One feature per branch**
- **Keep branches up to date** with main
- **Delete merged branches**

### Code Organization

- **Keep functions small** (< 50 lines)
- **Separate concerns** (routing, business logic, utilities)
- **Avoid global state** where possible
- **Use meaningful names**

### Security

- **Never commit secrets** (keys, passwords)
- **Validate all user input**
- **Sanitize file paths**
- **Use parameterized queries** (when adding database)
- **Keep dependencies updated**

### Performance

- **Profile before optimizing**
- **Use appropriate data structures**
- **Minimize I/O operations**
- **Cache when appropriate**
- **Monitor resource usage**

## Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [PEP 8 Style Guide](https://pep8.org/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [VLC Media Player](https://www.vlc.org/) - Stream playback testing
- [OBS Studio](https://obsproject.com/) - Stream testing and comparison

### Community
- GitHub Issues - Bug reports and feature requests
- Stack Overflow - General programming questions
- FFmpeg mailing list - FFmpeg-specific questions

## Conclusion

This guide should help you get started with YouTube Streamer development. For questions or issues not covered here, please:

1. Check existing GitHub issues
2. Review the codebase and comments
3. Open a new issue with detailed description

Happy coding!
