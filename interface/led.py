from random import randint
from time import sleep
import apa102
from gpiozero import LED as GPIO

# LED 控制模块
class LED:
    PIXELS_N=12

    def __init__(self):
        self.dev = apa102.APA102(num_led=self.PIXELS_N)
        self.power = GPIO(5)

    def switch(self, place, color : dict, bright):
        self.dev.set_pixel(place, color["r"], color["g"], color["b"], bright)
        self.dev.show()


if __name__ == "__main__":
    MyLED = LED()
    MyLED.power.on()
    for i in range(0, 12):
        MyLED.switch(i, {'r':randint(0, 255), 'g':randint(0, 255), 'b':randint(0, 255)}, 31)
        sleep(1)
        MyLED.switch(i, {'r':0, 'g':0, 'b':0}, 0)
