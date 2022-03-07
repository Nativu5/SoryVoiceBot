import os
from interface.led import LED as _LED
from interface.azure import parse_wav_file, recognize
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
            logger.info(
                recognize(audio_data, self.config.azure_key, "japaneast", "zh-CN"))
        except Exception as e:
            logger.warning(
                "Could not request results from Speech Recognition service; {0}".format(e))

        os.remove(fname)
        self.LED.power.off()
