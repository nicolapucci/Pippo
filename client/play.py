from collections import deque

import pygame
import io

volume = float(0.3)
audio_queue = deque()

pygame.mixer.init()
pygame.mixer.music.set_volume(volume)


def play_audio_bytes():
    while True:
        if audio_queue:
            mp3_chunk = audio_queue.popleft()
            try:
                audio_stream = io.BytesIO(mp3_chunk)
                pygame.mixer.music.load(audio_stream)
                pygame.mixer.music.play()
                
                # Aspettiamo la fine del chunk
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
            except Exception as e:
                print(f"Errore MP3: {e}")
        else:
            pygame.time.wait(10)
def add_to_queue(message:bytes):
    audio_queue.append(message)
    
def clear_queue():
    audio_queue.clear()

def get_volume():
    return volume

def low_volume():
    pygame.mixer.music.set_volume(float(0.1))

def default_volume():
    pygame.mixer.music.set_volume(volume)

def set_volume(new_volume:float):
    volume = new_volume
    pygame.mixer.music.set_volume(volume)