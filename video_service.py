from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# video_service.py
@app.get("/get-stream")
async def get_stream(video_id: str):
    try:
        cmd = [
            "yt-dlp",
            "-f", "best[height<=720]",
            "-g",
            f"https://youtu.be/{video_id}"
        ]
        
        # Timeout'u 90 saniyeye çıkardık
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=90
        )
        
        if result.returncode != 0:
            # Hata detayını HTTP response body'sine yazıyoruz
            print(f"yt-dlp ERROR: {result.stderr}") 
            raise HTTPException(status_code=400, detail=result.stderr)
            
        return {"url": result.stdout.strip()}

    except subprocess.TimeoutExpired:
        print("TIMEOUT: yt-dlp 90 saniyede cevap vermedi")
        raise HTTPException(status_code=504, detail="Sunucu yanıt süresi aşıldı. Lütfen tekrar deneyin.")
        
    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))