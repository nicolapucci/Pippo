import edge_tts
import uvicorn
from fastapi import FastAPI,Response

app = FastAPI()

@app.get("/")
async def text_to_speech_bytes(text:str):
    communicate = edge_tts.Communicate(text,"en-US-AriaNeural")
    audio_bytes = b""

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_bytes += chunk["data"]

    return Response(content=audio_bytes, media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)