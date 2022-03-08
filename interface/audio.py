import pyaudio
import wave
import time
from utils.log import init_logging

logger = init_logging(__name__)

def play_wav_file(fname):
    with wave.open(fname, 'rb') as wav_file:
        wav_data = wav_file.readframes(wav_file.getnframes())
    
    audio = pyaudio.PyAudio()
    
    logger.info("Start playing {}".format(fname))
    stream_out = audio.open(
        format=audio.get_format_from_width(wav_file.getsampwidth()),
        channels=wav_file.getnchannels(),
        rate=wav_file.getframerate(), input=False, output=True)

    stream_out.start_stream()
    stream_out.write(wav_data)

    time.sleep(0.2)

    stream_out.stop_stream()
    stream_out.close()
    audio.terminate()
