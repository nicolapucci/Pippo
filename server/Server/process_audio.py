import requests

import websockets
#stt
#nlu_router
#rag / action_handler
#llm / skip
#tts

stt_url = "http://stt:8000/"
tts_url = "http://tts:8000/"
ollama_url = "ws://ollama:8000/"
nlu_router_url = "http://NLU_Router:8000/"
rag_url = "http://rag:8000/"
action_handler_url = "http://action_handler/"

fallback_response = ''

async def get_chatbot_response(transcription,metadata):
    
    try:
        context = requests.post(url=rag_url,data={"request":transcription,"metadata":metadata})#obtain the context
    
        async with websockets.connect(f"{ollama_url}/ws") as ws:
            ws.send({"request":transcription,"context":context})
            done = False
            while not done:
                message = ws.receive()
                if "text" in message and message["text"] == 'done':
                    done = True
                else:
                    yield message
    except Exception as e:
        print(f"Error: {e}")



async def process_audio_and_get_response(audio):
    
    try:
        transcription = requests.post(url=stt_url,data=audio)#transcribe user's audio
        
        [type,metadata] = requests.get(url=nlu_router_url,params=transcription)#define the type of the request and relative metadatas

        if type == 'chat':

            for chunk in get_chatbot_response(transcription=transcription,metadata=metadata):
                audio_chunk = requests.get(url=tts_url,params=chunk)
                yield audio_chunk
            
        elif type == 'action':
            response = requests.post(url=action_handler_url,data=metadata)#perform the requested action if possible
            audio_response = requests.get(url=tts_url,params=response)
            yield audio_response
        
        else:
            audio_response = requests.get(url=tts_url,params=fallback_response)
            yield audio_response
        
    except requests.ConnectionError as e:
        print(f"Connection error: {e}")