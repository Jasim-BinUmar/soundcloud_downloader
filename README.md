## SoundCloudDownloader
Download songs directly from SoundCloud using Python and FFmpeg

# Dependencies
- Python 3.8+
- pip
- ffmpeg (system package)

### Installation

**Option 1: Using setup script (Recommended)**
```bash
./setup.sh
```

**Option 2: Manual setup**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Usage

**Console version:**
```bash
source venv/bin/activate
python main_console.py [SOUNDCLOUD_URL]
```

**GUI version:**
```bash
source venv/bin/activate
python main_ui.py
```

**API version:**
```bash
source venv/bin/activate
python run_api.py
```

The API will start on port 5000 by default (configurable via `PORT` environment variable).

### Example
```bash
source venv/bin/activate
python main_console.py "https://soundcloud.com/artist/track-name"
```

## API Usage

### Starting the API Server

```bash
source venv/bin/activate
python run_api.py
```

Or with a custom port:
```bash
PORT=8000 python run_api.py
```

### API Endpoints

#### GET /download
Download a SoundCloud track by URL query parameter.

**Request:**
```bash
curl "http://localhost:5000/download?url=https://soundcloud.com/artist/track-name" --output track.mp3
```

**Response:**
- Returns the MP3 file directly
- Content-Type: `audio/mpeg`
- Includes filename in Content-Disposition header

#### POST /download
Download a SoundCloud track by JSON body.

**Request:**
```bash
curl -X POST "http://localhost:5000/download" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://soundcloud.com/artist/track-name"}' \
  --output track.mp3
```

**Request Body:**
```json
{
  "url": "https://soundcloud.com/artist/track-name"
}
```

**Response:**
- Returns the MP3 file directly
- Content-Type: `audio/mpeg`
- Includes filename in Content-Disposition header

#### GET /
Get API information.

**Response:**
```json
{
  "message": "SoundCloud Downloader API",
  "endpoints": {
    "GET /download": "Download track by URL query parameter",
    "POST /download": "Download track by JSON body"
  }
}
```

### API Documentation

FastAPI provides automatic interactive API documentation:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

### Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success - MP3 file returned
- `500`: Server error - JSON response with error details

Example error response:
```json
{
  "detail": "Could not find track data in SoundCloud response"
}
```

### Notes
- The downloader uses HLS streams and converts them to MP3
- Console/GUI downloads are saved in the current directory
- API downloads are saved in the `downloads/` directory
- Make sure ffmpeg is installed on your system (`sudo apt install ffmpeg` on Ubuntu/Debian)  
