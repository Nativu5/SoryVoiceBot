from time import sleep
from interface import apa102
from utils.log import init_logging
from gpiozero import LED as GPIO
import threading

# LED 控制模块
logger = init_logging(__name__)

class LEDController:
    PIXELS_N = 12

    def __init__(self):
        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        self.power = GPIO(5)

    def switch(self, pattern: dict[int, list]):
        for (num, value) in pattern.items():
            if num < 0 or num >= self.PIXELS_N:
                raise ValueError("Invalid LED number!")
            try:
                self.dev.set_pixel(num, value[0], value[1], value[2], value[3])
            except IndexError:
                raise IndexError("Invalid LED property!")

        self.dev.show()

    def switch_by_place(self, place: int, color: dict, bright):
        self.dev.set_pixel(place, color["r"], color["g"], color["b"], bright)
        self.dev.show()

    def _rotate_lights(self, count, time=0.25):
        while count > 0:
            self.dev.rotate()
            self.dev.show()
            sleep(time)
            count -= 1
        self.dev.clear_strip()
    
    def circulate_lights(self, color, bright):
        self.dev.set_pixel(0, color["r"], color["g"], color["b"], bright)
        th_rotate_lights = threading.Thread(target=self._rotate_lights, args=(24, 0.1))
        th_rotate_lights.start()
