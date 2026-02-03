from fastapi import FastAPI, Request
from faster_whisper import WhisperModel
import io
import numpy as np
import uvicorn

app = FastAPI()
model = WhisperModel("base", device="cpu", compute_type="int8")

@app.post("/")
async def transcribe(request: Request):
    audio_data = await request.body()
    
    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

    segments, _ = model.transcribe(audio_np, beam_size=5)
    
    text = " ".join([s.text for s in segments]).strip()
    return {"text": text}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)