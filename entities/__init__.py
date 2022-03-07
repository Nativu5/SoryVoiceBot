import speech_recognition as sr
import os
from interface.led import LED as _LED

class Sory:
    def __init__(self, detector, led : _LED, config) -> None:
        self.detector = detector
        self.LED = led
        self.config = config

    def detected_callback(self, fname: str = ""):
        # snowboydecoder.play_audio_file()
        self.LED.power.on()
        for i in range(0, 12):
            self.LED.switch_by_place(i, color={"r": 255, "g": 0, "b": 0}, bright=30)
        print('Recording audio...', end='', flush=True)

    def audioRecorderCallback(self, fname):
        print("converting audio to text")
        r = sr.Recognizer()
        with sr.AudioFile(fname) as source:
            audio = r.record(source)
        try:
            print(r.recognize_bing(audio_data=audio, key=self.config.azure_key, language='zh-CN'))
            # print(r.recognize_google(audio, language="zh-yue"))
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Speech Recognition service; {0}".format(e))

        os.remove(fname)
        self.LED.power.off()
