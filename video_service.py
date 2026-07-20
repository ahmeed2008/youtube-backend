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

@app.get("/get-stream")
async def get_stream(video_id: str):
    try:
        cmd = [
            "yt-dlp",
            "-f", "best[height<=720]",
            "-g",
            f"https://youtu.be/{video_id}"
        ]
        
        # Asenkron çalıştırarak timeout'u doğru yönetiyoruz
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=90)
        except asyncio.TimeoutError:
            proc.kill()
            raise HTTPException(status_code=504, detail="Sunucu yanıt süresi aşıldı. Lütfen tekrar deneyin.")

        if proc.returncode != 0:
            error_msg = stderr.decode().strip()
            print(f"YT-DLP ERROR: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
            
        return {"url": stdout.decode().strip()}

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))