# YouTube Streamer - Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Design](#component-design)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Patterns](#design-patterns)
7. [Security Considerations](#security-considerations)
8. [Performance Considerations](#performance-considerations)

## Overview

YouTube Streamer is a web-based application designed to stream video content to RTMP platforms (YouTube Live, Twitch, Facebook Live, etc.). The application follows a client-server architecture with a Flask backend and a browser-based frontend.

### Key Characteristics
- **Language**: Python 3.7+
- **Architecture**: Client-Server (Web-based)
- **Concurrency Model**: Multi-process (one FFmpeg process per stream)
- **Communication**: RESTful API with JSON payloads
- **Deployment**: Standalone Flask development server

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Web Browser (HTML/CSS/JavaScript)            │  │
│  │  - Stream configuration forms                        │  │
│  │  - Active stream management UI                       │  │
│  │  - jQuery for AJAX communication                     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Flask Web Server (app.py)               │  │
│  │  - REST API endpoints                                │  │
│  │  - Request validation                                │  │
│  │  - Stream lifecycle management                       │  │
│  │  - In-memory stream registry                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Processing Layer                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Streaming Module (streamer.py)              │  │
│  │  - FFmpeg process management                         │  │
│  │  - File validation                                   │  │
│  │  - Command generation                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ subprocess
┌─────────────────────────────────────────────────────────────┐
│                        Media Layer                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               FFmpeg Processes                       │  │
│  │  - Video encoding (H.264)                            │  │
│  │  - Audio encoding (AAC)                              │  │
│  │  - Stream multiplexing                               │  │
│  │  - RTMP transmission                                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ RTMP
┌─────────────────────────────────────────────────────────────┐
│                      External Services                       │
│  - YouTube Live                                              │
│  - Twitch                                                    │
│  - Facebook Live                                             │
│  - Other RTMP platforms                                      │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Flask Web Server (`app.py`)

**Purpose**: Serves as the main application entry point and HTTP API server.

**Responsibilities**:
- Serve the web interface (`index.html`)
- Handle REST API requests
- Manage stream lifecycle (create, destroy)
- Maintain registry of active streams
- Validate request parameters
- Handle errors and return JSON responses

**Key Components**:
```python
streams: Dict[str, Dict[str, Any]]  # Global stream registry
    Key: stream_id (str)
    Value: {
        'process': subprocess.Popen,  # FFmpeg process
        'config': {                   # Stream configuration
            'video_file': str,
            'audio_file': str,
            'stream_url': str,
            'stream_key': str
        }
    }
```

**API Endpoints**:
- `GET /` - Serve web interface
- `POST /start_stream` - Create and start a new stream
- `POST /stop_stream` - Stop and destroy a stream
- `GET /list_streams` - List all active stream IDs

### 2. Streaming Module (`streamer.py`)

**Purpose**: Manages FFmpeg process lifecycle and video encoding.

**Responsibilities**:
- Verify FFmpeg installation
- Validate media file existence
- Generate FFmpeg command strings
- Start FFmpeg subprocess
- Terminate FFmpeg processes gracefully

**Key Functions**:
- `check_ffmpeg()` - Verify FFmpeg availability
- `start_streaming(config)` - Launch FFmpeg process with configuration
- `stop_streaming(process)` - Terminate FFmpeg process
- `get_config()` - [Legacy] Load configuration from file

**FFmpeg Configuration**:
```
Video Encoding:
- Codec: H.264 (libx264)
- Preset: veryfast
- Bitrate: 3000k (max)
- Buffer: 6000k
- Pixel Format: yuv420p
- GOP Size: 50 frames

Audio Encoding:
- Codec: AAC
- Bitrate: 160k
- Channels: 2 (stereo)
- Sample Rate: 44100 Hz

Streaming:
- Protocol: RTMP/FLV
- Loop: Indefinite (-stream_loop -1)
- Timing: Real-time (-re)
```

### 3. Web Interface (`templates/index.html`)

**Purpose**: Provide user interface for stream management.

**Responsibilities**:
- Display stream configuration form
- List active streams
- Send AJAX requests to backend
- Update UI based on responses

**Technologies**:
- HTML5 for structure
- jQuery for AJAX and DOM manipulation
- Inline JavaScript for event handling

### 4. Desktop GUI (`gui.py`)

**Status**: Legacy/Deprecated

**Purpose**: Originally provided a PyQt5 desktop interface.

**Current State**: Not compatible with current streaming implementation; kept for reference.

## Data Flow

### Stream Creation Flow

```
1. User fills form in browser
   ├─ Stream ID
   ├─ Video file path
   ├─ Audio file path
   ├─ RTMP URL
   └─ Stream key

2. JavaScript sends POST to /start_stream
   └─ JSON payload with configuration

3. Flask endpoint validates request
   ├─ Check all parameters present
   ├─ Verify stream ID is unique
   └─ Build stream_config dict

4. Call start_streaming(stream_config)
   ├─ Validate audio file exists
   ├─ Validate video file exists
   ├─ Generate FFmpeg command
   └─ Start subprocess.Popen

5. Store process in global streams dict
   └─ streams[stream_id] = {'process': ..., 'config': ...}

6. Return success JSON response
   └─ {"status": "success", "message": "..."}

7. Update browser UI
   └─ Add stream to active list
```

### Stream Termination Flow

```
1. User clicks "Stop" button
   └─ JavaScript sends POST to /stop_stream

2. Flask validates stream exists
   └─ Check stream_id in streams dict

3. Call stop_streaming(process)
   ├─ Send SIGTERM to FFmpeg
   └─ Wait for process to exit

4. Remove from streams dict
   └─ del streams[stream_id]

5. Return success JSON response
   └─ {"status": "success", "message": "..."}

6. Update browser UI
   └─ Remove stream from active list
```

### Media Processing Flow (within FFmpeg)

```
┌──────────────┐
│ Video File   │ ─┐
│ (looping)    │  │
└──────────────┘  │
                  ├─► ┌──────────────┐
┌──────────────┐  │   │   FFmpeg     │
│ Audio File   │ ─┘   │ ┌──────────┐ │
│ (looping)    │      │ │ Video    │ │  ┌────────────┐
└──────────────┘      │ │ Decode   │ │  │            │
                      │ └────┬─────┘ │  │   RTMP     │
                      │      │       │  │   Stream   │
                      │ ┌────▼─────┐ │  │  (YouTube, │
                      │ │ Video    │ ├─►│   Twitch,  │
                      │ │ Encode   │ │  │   etc.)    │
                      │ │ (H.264)  │ │  │            │
                      │ └────┬─────┘ │  └────────────┘
                      │      │       │
                      │ ┌────▼─────┐ │
                      │ │ Audio    │ │
                      │ │ Decode   │ │
                      │ └────┬─────┘ │
                      │      │       │
                      │ ┌────▼─────┐ │
                      │ │ Audio    │ │
                      │ │ Encode   │ │
                      │ │ (AAC)    │ │
                      │ └────┬─────┘ │
                      │      │       │
                      │ ┌────▼─────┐ │
                      │ │   Mux    │ │
                      │ │  (FLV)   │ │
                      │ └──────────┘ │
                      └──────────────┘
```

## Technology Stack

### Backend
- **Python 3.7+**: Application language
- **Flask 2.3.2**: Web framework
- **Werkzeug 3.0.1**: WSGI utility library (Flask dependency)

### Frontend
- **HTML5**: Page structure
- **CSS3**: Styling
- **JavaScript (ES6)**: Client-side logic
- **jQuery 3.6.0**: AJAX and DOM manipulation (CDN)

### External Dependencies
- **FFmpeg**: Video/audio encoding and streaming
  - Not a Python package
  - Must be installed separately
  - Required version: Any modern version (4.0+)

### Optional/Legacy
- **PyQt5**: Desktop GUI framework (not in requirements.txt)
- **ConfigParser**: INI file parsing (unused in current implementation)

## Design Patterns

### 1. **Repository Pattern**
The `streams` dictionary acts as an in-memory repository for active stream state:
```python
streams: Dict[str, Dict[str, Any]] = {}
```

**Pros**:
- Fast access (O(1) lookups)
- Simple implementation

**Cons**:
- Non-persistent (lost on restart)
- Not thread-safe for multi-worker deployments

### 2. **Facade Pattern**
The `streamer.py` module provides a simplified interface to complex FFmpeg operations:
```python
# Complex FFmpeg command hidden behind simple function
process = start_streaming(stream_config)
```

### 3. **Process per Stream**
Each stream runs as an independent subprocess:

**Benefits**:
- Isolation: One stream failure doesn't affect others
- Scalability: Limited only by system resources
- Simplicity: No complex multiplexing logic

**Drawbacks**:
- Resource overhead: Each process has its own memory/CPU
- No shared resources between streams

### 4. **RESTful API Design**
API follows REST principles:
- Resources: Streams
- Operations: Create (POST), Read (GET), Delete (POST)
- Stateless: Each request contains all necessary information
- JSON: Standard data format

## Security Considerations

### Current Security Posture

**Vulnerabilities**:
1. **No Authentication**: Anyone with network access can control streams
2. **No Authorization**: No user/permission system
3. **Path Traversal**: User-supplied file paths not sanitized
4. **No HTTPS**: Credentials transmitted in plain text
5. **Command Injection**: File paths passed to shell (mitigated by `shlex.split()`)
6. **No Rate Limiting**: Vulnerable to abuse/DoS
7. **Stream Keys in Logs**: Keys logged in debug mode

### Recommended Security Enhancements

1. **Add Authentication**:
   ```python
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   ```

2. **Validate File Paths**:
   ```python
   import os
   file_path = os.path.realpath(user_input)
   if not file_path.startswith(ALLOWED_DIRECTORY):
       raise ValueError("Invalid path")
   ```

3. **Use Environment Variables for Secrets**:
   ```python
   import os
   STREAM_KEY = os.environ.get('YOUTUBE_STREAM_KEY')
   ```

4. **Deploy Behind Reverse Proxy**:
   - Use nginx or Apache with SSL/TLS
   - Implement rate limiting at proxy level

5. **Sanitize Logging**:
   ```python
   # Mask stream keys in logs
   safe_key = stream_key[:4] + "****"
   ```

## Performance Considerations

### Scalability Limits

**Per-Stream Resources**:
- CPU: ~5-15% per stream (varies by preset)
- Memory: ~50-200MB per FFmpeg process
- Network: ~3 Mbps upload per stream

**Theoretical Limits** (on typical server):
- 8-core CPU: ~10-15 concurrent streams
- 16GB RAM: ~30-40 streams
- 100 Mbps uplink: ~30 streams

### Bottlenecks

1. **CPU Encoding**: Video encoding is CPU-intensive
   - Solution: Use hardware encoding (NVENC, QuickSync)
   - Trade-off: Quality vs. performance

2. **Upload Bandwidth**: Each stream requires sustained upload
   - Solution: Monitor and limit concurrent streams
   - Alternative: Reduce bitrate/quality

3. **Disk I/O**: Reading multiple video files simultaneously
   - Solution: Use SSD storage
   - Alternative: Pre-load files into RAM

### Optimization Strategies

1. **Hardware Encoding**:
   ```bash
   # Use NVIDIA GPU encoding
   -c:v h264_nvenc -preset fast
   ```

2. **Adjust Presets**:
   ```python
   # Current: veryfast (moderate CPU)
   # Faster: ultrafast (low CPU, lower quality)
   # Better: faster, fast (higher CPU, better quality)
   ```

3. **Stream Limits**:
   ```python
   MAX_CONCURRENT_STREAMS = 10
   if len(streams) >= MAX_CONCURRENT_STREAMS:
       return jsonify({"error": "Maximum streams reached"})
   ```

4. **Production Deployment**:
   - Use Gunicorn/uWSGI with multiple workers
   - Deploy behind nginx for static files
   - Use supervisor for process management
   - Implement horizontal scaling with load balancer

### Monitoring

**Key Metrics to Track**:
- Active stream count
- CPU usage per stream
- Memory consumption
- Upload bandwidth utilization
- FFmpeg process status
- API response times

**Recommended Tools**:
- Prometheus + Grafana for metrics
- ELK stack for log aggregation
- systemd for process monitoring

## Future Architecture Considerations

### Potential Improvements

1. **Persistent Storage**:
   - Add database (SQLite/PostgreSQL)
   - Store stream configurations
   - Track streaming history

2. **Stream Health Monitoring**:
   - Monitor FFmpeg stderr for errors
   - Auto-restart failed streams
   - Alert on stream failures

3. **Microservices Architecture**:
   - Separate API service from encoding workers
   - Use message queue (RabbitMQ, Redis)
   - Enable horizontal scaling

4. **WebSocket Updates**:
   - Real-time stream status updates
   - Live log streaming to browser

5. **Container Deployment**:
   - Docker containerization
   - Kubernetes orchestration
   - Cloud-native deployment

### Architectural Evolution Path

```
Current State → Phase 1 → Phase 2 → Phase 3
Monolith      Database   Workers    Cloud-Native

Single        + SQLite   + Message  + Kubernetes
Process       + Auth     Queue      + Auto-scaling
              + Health   + Separate + Multi-region
                Check    Encoders   + CDN
```

## Conclusion

The YouTube Streamer architecture is designed for simplicity and ease of deployment. It's well-suited for small-scale streaming operations (1-10 concurrent streams). For production use at scale, consider the security and performance enhancements outlined in this document.

### Strengths
- Simple, understandable design
- Easy to deploy and modify
- Independent stream isolation
- RESTful API design

### Weaknesses
- No persistent storage
- Limited scalability
- Minimal security features
- No monitoring/observability

### Best Use Cases
- Personal streaming projects
- Small teams/organizations
- Development and testing
- Educational purposes

For enterprise deployments, significant enhancements to security, scalability, and reliability are recommended.
