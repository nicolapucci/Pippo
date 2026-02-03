from fastapi import (
    FastAPI,
    Websocket
)
import uvicorn
from ollama import AsyncClient


OLLAMA_URL = "http://host.docker.internal:11434"
client = AsyncClient(host=OLLAMA_URL)


app = FastAPI()

@app.websocket('/ws')
async def chat(websocket:Websocket):
    
    messages = websocket.receive()

    response = await client.chat(
        model='gemma3:4b',
        messages=messages,
        stream=True
    )

    async for chunk in response:
        yield chunk['message']['content']


@app.post('/generate')
async def generate(prompt:str):
    response = await client.generate(
        model='gemma3:4b', 
        prompt=prompt
    )
    return response['response'].strip().replace('"', '')

