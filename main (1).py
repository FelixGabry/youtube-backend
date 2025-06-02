from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yt_dlp
import os
import uuid
from pathlib import Path
import asyncio
from typing import Dict

app = FastAPI(title="YouTube Downloader Backend")

# Configura CORS per il tuo dominio Lovable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione: ["https://your-lovable-domain.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory per i download
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

# Storage per tracking downloads
downloads_status: Dict[str, dict] = {}

@app.post("/api/youtube/download")
async def start_youtube_download(request: dict, background_tasks: BackgroundTasks):
    url = request.get("url")
    format_type = request.get("format", "mp4")
    quality = request.get("quality", "720p")
    
    if not url:
        raise HTTPException(status_code=400, detail="URL richiesto")
    
    download_id = str(uuid.uuid4())
    
    # Inizializza lo status
    downloads_status[download_id] = {
        "status": "processing",
        "progress": 0,
        "title": None,
        "download_url": None,
        "error": None
    }
    
    # Avvia download in background
    background_tasks.add_task(process_youtube_download, download_id, url, format_type, quality)
    
    return {
        "success": True,
        "download_id": download_id,
        "status": "processing"
    }

async def process_youtube_download(download_id: str, url: str, format_type: str, quality: str):
    try:
        # Configura yt-dlp
        if format_type == "mp3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{DOWNLOAD_DIR}/{download_id}.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            format_selector = f'best[height<={quality[:-1]}]' if quality != "best" else "best"
            ydl_opts = {
                'format': format_selector,
                'outtmpl': f'{DOWNLOAD_DIR}/{download_id}.%(ext)s',
            }
        
        # Download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
        
        # Trova file scaricato
        downloaded_files = list(DOWNLOAD_DIR.glob(f"{download_id}.*"))
        if downloaded_files:
            downloads_status[download_id] = {
                "status": "completed",
                "progress": 100,
                "title": title,
                "download_url": f"/api/file/{download_id}",
                "error": None
            }
        else:
            raise Exception("File non trovato dopo download")
            
    except Exception as e:
        downloads_status[download_id] = {
            "status": "failed",
            "progress": 0,
            "title": None,
            "download_url": None,
            "error": str(e)
        }

@app.get("/api/download/status/{download_id}")
async def get_download_status(download_id: str):
    if download_id not in downloads_status:
        raise HTTPException(status_code=404, detail="Download non trovato")
    
    return downloads_status[download_id]

@app.get("/api/file/{download_id}")
async def download_file(download_id: str):
    files = list(DOWNLOAD_DIR.glob(f"{download_id}.*"))
    if not files:
        raise HTTPException(status_code=404, detail="File non trovato")
    
    file_path = files[0]
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type='application/octet-stream'
    )

@app.get("/")
async def root():
    return {"message": "YouTube Downloader Backend is running!", "status": "active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)