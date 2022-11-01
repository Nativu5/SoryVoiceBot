import utils.config
import utils.log
import snowboy
from entities import Sory
from entities.LEDController import LEDController
from entities.MusicProvider import CloudMusicProvider, LocalMusicProvider
from entities.STTProvider import AzureSTTProvider, LocalSTTProvider
from entities.TTSProvider import AzureTTSProvider
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

    led_control = LEDController()
    led_control.power.on()
    led_control.circulate_lights(color={"r": 255, "g": 0, "b": 0}, bright=15)

    detector = snowboy.get_detector(
        [config.hotword, config.hotword2], sensitivity=config.sensitivity)

    music_provider = CloudMusicProvider(
        base_url=config.netease_api_url, email=config.netease_email, md5_password=config.netease_password_md5)
    stt_provider = AzureSTTProvider(
        key=config.azure_key, region=config.azure_region)
    tts_provider = AzureTTSProvider(
        key=config.azure_key, region=config.azure_region)

    bot = Sory(config=config, detector=detector, led=led_control,
               music=music_provider, stt=stt_provider, tts=tts_provider)

    logger.info("Sory Bot is listening.")
    bot.detector.start(detected_callback=[bot.detected_callback, bot.dectected_stop],
                       audio_recorder_callback=bot.audio_recorder_callback,
                       interrupt_check=interrupt_callback,
                       silent_count_threshold=6,
                       sleep_time=0.01)

    bot.detector.terminate()
    led_control.dev.cleanup()
    led_control.power.off()