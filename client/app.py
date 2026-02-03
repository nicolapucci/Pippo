import asyncio
import websockets
from datect_wake_word_and_record_user import wake_word_task
import threading
from play import (
    play_audio_bytes,
    add_to_queue
)


audio_thread = threading.Thread(target=play_audio_bytes, daemon=True)#<-- whenever it finds something in the audio_queue he will play it
audio_thread.start()


async def listen_to_websocket(websocket:websockets.ClientConnection):#<-- he works as a router for the messages received through the websocket
    while True:
        try:
            message = await asyncio.wait_for(websocket.recv(),timeout=1.0)
            if isinstance(message,bytes):
                add_to_queue(message)#<-- add the received message to the audio_queue
                await asyncio.sleep(0.1)
            elif isinstance(message,str):
                print(f"string received: {message}")
                if message == 'done':#?????
                    print("done")#tmp
        except asyncio.TimeoutError:
            continue


async def main():
    uri = "ws://127.0.0.1:8000/ws"
    
    while True:#<-- if there is an error in connection he tries to reconnect
        try:
            async with websockets.connect(uri) as websocket:
                print("Connesso al server!")

                asyncio.create_task(wake_word_task(websocket)) #<-- w8 in the background for the wake word, if activated starts recording and send data to server
                await listen_to_websocket(websocket) #<-- keep listening to the websocket, main thread

        except websockets.ConnectionClosed as e:
            print(f"Errore di connessione: {e}")
            await asyncio.sleep(1)#<-- w8 b4 tring to reconnect

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("stopping..")
        exit()