from time import sleep
from interface import apa102
from utils import init_logging
from gpiozero import LED as GPIO
import threading

PIXELS_N = 12
RED = {"r": 255, "g": 0, "b": 0}
GREEN = {"r": 0, "g": 255, "b": 0}
BLUE = {"r": 0, "g": 0, "b": 255}

logger = init_logging(__name__)

class LEDController:

    def __init__(self):
        self.dev = apa102.APA102(num_led=PIXELS_N)
        self.power = GPIO(pin=5)

    def switch(self, pattern: dict[int, list]):
        for (num, value) in pattern.items():
            if num < 0 or num >= PIXELS_N:
                raise ValueError("Invalid LED number!")
            try:
                self.dev.set_pixel(num, value[0], value[1], value[2], value[3])
            except IndexError:
                raise IndexError("Invalid LED property!")

        self.dev.show()
    
    def set_all_lights(self, color, bright):
        for i in range(0, PIXELS_N):
            self.dev.set_pixel(i, color["r"], color["g"], color["b"], bright)
        self.dev.show()

    def _rotating(self, interrupt, lapse):
        while True:
            if interrupt():
                return
            self.dev.rotate()
            self.dev.show()
            sleep(lapse)
    
    def circulate_lights(self, color, bright, lapse):
        self.dev.clear_strip()
        self.dev.set_pixel(0, color["r"], color["g"], color["b"], bright)
        self.dev.show()
        th_stop = False
        th_rotate_lights = threading.Thread(target=self._rotating, args=(lambda: th_stop, lapse))
        th_rotate_lights.start()

        def set_stop():
            nonlocal th_stop
            th_stop = True
            th_rotate_lights.join()
            self.dev.clear_strip()

        return set_stop
    
    def _breathing(self, interrupt, color, max_bright, step, lapse):
        bright_grades = range(1, max_bright, step)
        bright_grades = list(bright_grades) + list(reversed(bright_grades))
        while True:
            for bright in bright_grades:
                if interrupt():
                    return
                self.set_all_lights(color, bright)
                sleep(lapse)
    
    def breathing_lights(self, color, max_bright=30, step=1, lapse=0.020):
        self.dev.clear_strip()
        th_stop = False
        th_breathing_lights = threading.Thread(target=self._breathing, args=(lambda: th_stop, color, max_bright, step, lapse))
        th_breathing_lights.start()
        
        def set_stop():
            nonlocal th_stop
            th_stop = True
            th_breathing_lights.join()
            self.dev.clear_strip()

        return set_stop
