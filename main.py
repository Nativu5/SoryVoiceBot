import utils.config
import utils.log
import snowboy
from entities import Sory
from interface.led import LED

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


if __name__ == '__main__':
    config = utils.config.Config("config.yaml")
    config.load_all()

    logger = utils.log.init_logging(name=__name__)

    detector = snowboy.get_detector(config.hotword, sensitivity=0.42)

    myLED = LED()

    bot = Sory(detector=detector, led=myLED, config=config)

    bot.detector.start(detected_callback=bot.detected_callback,
                       audio_recorder_callback=bot.audio_recorder_callback,
                       interrupt_check=interrupt_callback,
                       silent_count_threshold=12,
                       sleep_time=0.01)

    bot.detector.terminate()
