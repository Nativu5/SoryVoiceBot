from random import randint
from re import M
from time import sleep
import apa102
from gpiozero import LED as GPIO

# LED 控制模块


class LED:
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
        self.dev.set_pixel(place, color["r"], color["g"], color["b"], 50)
        self.dev.show()
        # self.switch(pattern={place: [color["r"], color["g"], color["b"], bright]})


if __name__ == "__main__":
    MyLED = LED()
    MyLED.power.on()
    for i in range(0, 12):
        MyLED.switch_by_place(
            i, {'r': randint(0, 255), 'g': randint(0, 255), 'b': randint(0, 255)}, 31)
        sleep(1)
        # MyLED.switch({i: [255, 255, 0, 0]})
    MyLED.power.off()
