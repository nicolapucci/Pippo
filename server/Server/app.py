from fastapi import (
    FastAPI,
    WebSocket
)
from process_audio import process_audio_and_get_response

import uvicorn
import asyncio

app = FastAPI()
audio_input_buffer = bytearray()

@app.websocket('/ws')
async def main(websocket:WebSocket):
    await websocket.accept()

    global audio_input_buffer

    while True:
        message = await websocket.receive()

        if message['type'] == 'websocket.disconnect':
            print("Disconnecting...")
            break

        if "bytes" in message:
            audio_input_buffer += message['bytes']

        elif "text" in message:
            command = message["text"]

            if command == 'done':
                try:
                    for chunk in process_audio_and_get_response(audio=audio_input_buffer):
                        websocket.send_bytes(chunk)
                except Exception as e:
                    print(f"Error: {e}")



if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0',port=8000)
