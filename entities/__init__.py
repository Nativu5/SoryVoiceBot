import os
from interface.led import LED as _LED
from interface.azure import parse_wav_file, speech_to_text, text_to_speech
from interface.audio import play_wav_file
from utils.log import init_logging

logger = init_logging(__name__)


class Sory:
    def __init__(self, detector, led: _LED, config) -> None:
        self.detector = detector
        self.config = config
        self.LED = led

    def detected_callback(self, fname: str = ""):
        self.LED.power.on()
        for i in range(0, 12):
            self.LED.switch_by_place(
                i, color={"r": 255, "g": 0, "b": 0}, bright=30)
        print('Recording audio...', end='', flush=True)

    def audio_recorder_callback(self, fname):
        print("Converting audio to text")
        try:
            audio_data = parse_wav_file(fname)
            stt_text = speech_to_text(audio_data, self.config.azure_key, "japaneast", "zh-CN")
            logger.info(stt_text)
        except Exception as e:
            logger.warning(
                "Could not request results from Speech Recognition service; {0}".format(e))
        else:
            play_back_data = text_to_speech(stt_text, self.config.azure_key, "japaneast", "playback_" + fname)
            play_wav_file("playback_" + fname)

        os.remove(fname)
        os.remove("playback_" + fname)
        self.LED.power.off()
