from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import logging
from api_service import download_track

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SoundCloud Downloader API", version="1.0.0")


class DownloadRequest(BaseModel):
    url: str


@app.get("/")
async def root():
    return {
        "message": "SoundCloud Downloader API",
        "endpoints": {
            "GET /download": "Download track by URL query parameter",
            "POST /download": "Download track by JSON body"
        }
    }


@app.get("/download")
async def download_get(url: str = Query(..., description="SoundCloud track URL")):
    try:
        logger.info(f"Download request received for URL: {url}")
        file_path = download_track(url)
        filename = os.path.basename(file_path)
        logger.info(f"Download successful: {filename}")
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download")
async def download_post(request: DownloadRequest):
    try:
        logger.info(f"Download request received for URL: {request.url}")
        file_path = download_track(request.url)
        filename = os.path.basename(file_path)
        logger.info(f"Download successful: {filename}")
        return FileResponse(
            file_path,
            media_type="audio/mpeg",
            filename=filename,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    except Exception as e:
        logger.error(f"Download failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

