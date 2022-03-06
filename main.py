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
    config.read()

    logger = utils.log.init_logging(config.log_level)
    logger.warning(config)
 
    # snowboy.keyword.start_loop(model=config.hotword)
    detector = snowboy.get_detector(config.hotword)

    myLED = LED()

    bot = Sory(detector=detector, led=myLED)

    detector.start(detected_callback=bot.detected_callback,
                   audio_recorder_callback=bot.audioRecorderCallback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.01)

    detector.terminate()
    