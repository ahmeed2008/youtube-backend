from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-stream")
async def get_stream(video_id: str):
    try:
        cmd = [
            "yt-dlp",
            "-f", "best[height<=720]",
            "-g",
            f"https://youtu.be/{video_id}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            raise HTTPException(status_code=400, detail=result.stderr)
            
        return {"url": result.stdout.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))