from pvrecorder import PvRecorder
import pvporcupine
import struct
import asyncio
import os
from dotenv import load_dotenv

from play import (
    low_volume,
    default_volume,
    clear_queue
)

load_dotenv()

volume = 0.3
PICOVOICE_API_KEY = os.getenv('PICOVOICE_API_KEY')

#when detects the wake word returns true
def listen_for_wake_word():
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_API_KEY,
        keywords=['picovoice','bumblebee']
    )
    recorder = PvRecorder(device_index=1,frame_length=porcupine.frame_length)
    try:
        recorder.start()
        while True:
            pcm = recorder.read()
            keyword_index = porcupine.process(pcm)
            if keyword_index >= 0:
                print("Wake Word detected!")
                return True
    finally:
        recorder.stop()
        porcupine.delete()

#register the user and send a stream through the websocket, when registration is done it sends the string done.
async def register_user(websocket):
    low_volume()#<-- lower the volume of what is being played to record the user while waiting for the queue to be cleared
    recorder = PvRecorder(device_index=1,frame_length=512)
    recorder.start()
    silence_threshold = 30
    silent_frames = 0
    try:
        await websocket.send("stop")#<-- tells server to stop any active task
        clear_queue()#<-- clear queue after the server has stopped sending packages to ensure the queue will stay clean until next communication
        print(f"Now listening....")
        while True:
            frame = recorder.read()
            binary_data = struct.pack("h" * len(frame), *frame)
            await websocket.send(bytes(binary_data))#<-- send recording to server
            rms = sum(abs(x) for x in frame) /len(frame)
            if rms < 50:
                silent_frames += 1
            else:
                silent_frames = 0
            if silent_frames > silence_threshold:
                print("Elaborating request...")
                await websocket.send("done")#<-- tells server that recording is over
                await asyncio.sleep(0.1)
                break
    finally:
        recorder.stop()
        recorder.delete()
        default_volume()#<-- returns the audio volume to the default

#sits in the background w8ing for the wake word, when it hears it it launches register_user, once the registration is done it goes back to w8ing for the wake word
async def wake_word_task(websocket):
    loop = asyncio.get_event_loop()
    while True:
        detected = await loop.run_in_executor(None, listen_for_wake_word)
        
        if detected:
            await register_user(websocket)
            print("registration is completed")
            await asyncio.sleep(0.1)