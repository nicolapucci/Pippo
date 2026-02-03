import requests
from fastapi import (
    FastAPI
    )
import uvicorn
import os
import re
from pydantic import BaseModel


class RequestBody(BaseModel):
    message: str
    chat_history: list


ALLOWED_INTENTS = []
ALLOWED_SLOTS = []

app = FastAPI()

ollama_url = 'http://ollama/generate'

def reformat_response(response):
    splits = re.split('\|',response)

    msg_type = splits[0]
    data = {}
    for split in splits:
        if ':' in split:
            [key,value] = re.split('\:',split,maxsplit=1)
            data[key] = value

    return [msg_type,data]
    

def get_prompt(message,chat_history):
    return f"""
                            Given the conversation history and the user's follow-up question, classify the request.
                            You must respond ONLY with the classification string. NO explanation.

                            **TYPES**: 
                            - CHAT: Use if the user wants to talk, ask info, or general knowledge.
                            - ACTION: Use if the user wants to perform an operation (play music, lights, etc.).

                            **ALLOWED INTENTS**: {ALLOWED_INTENTS}
                            **ALLOWED SLOTS**: {ALLOWED_SLOTS}

                            **RULES**:
                            1. If CHAT, format: CHAT|collection:collection_name
                            2. If ACTION, format: ACTION|intent:intent_name|slot_name:value|slot_name:value
                            3. If no specific collection or slots, use 'none'.

                            **RESPONSE EXAMPLES**:
                            ACTION|play_music|artist:linkin park
                            CHAT|technical_manual
                            CHAT|none

                            **USER QUESTION**: {message}
                            **CONVERSATION HISTORY**: {chat_history}
            """

@app.post('/')
async def main(body:RequestBody):

    prompt = get_prompt(body.message,body.chat_history)
    try:
        response = requests.post(url=ollama_url,data={"prompt":prompt})
        
        return reformat_response(response)
    except requests.ConnectionError as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    uvicorn.run(app,host='0.0.0.0',port=8000)