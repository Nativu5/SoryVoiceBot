from interface.hainterface import HAInterface
import utils
from snowboy import get_detector
from signal import signal, SIGTERM, SIGINT
from entities import Sory
from entities.LEDController import LEDController, RED
from entities.MusicProvider import CloudMusicProvider, LocalMusicProvider
from entities.STTProvider import AzureSTTProvider, LocalSTTProvider
from entities.TTSProvider import AzureTTSProvider
from interface.audio import VLCInterface

interrupted = False


def signal_handler(signal, frame):
    """Do clean up when exiting"""
    global interrupted
    interrupted = True
    logger.warning("Received exit signal, now cleaning up and exiting...")
    led_control.power.off()
    led_control.dev.cleanup()
    exit()


def interrupt_callback():
    global interrupted
    return interrupted


if __name__ == '__main__':
    # Add handler for exit signals
    signal(SIGTERM, signal_handler)
    signal(SIGINT, signal_handler)

    config = utils.Config("config.yaml")
    config.load_all()

    logger = utils.init_logging(__name__)

    audio_player = VLCInterface()
    audio_player.play_audio('resources/aloha.wav')

    led_control = LEDController()
    led_control.power.on()
    stop_circulate = led_control.circulate_lights(
        color=RED, bright=15, lapse=0.1)

    detector = get_detector(
        config.hotword, sensitivity=config.sensitivity)

    music_provider = CloudMusicProvider(
        base_url=config.netease_api_url, email=config.netease_email, md5_password=config.netease_password_md5)
    stt_provider = AzureSTTProvider(
        key=config.azure_key, region=config.azure_region)
    tts_provider = AzureTTSProvider(
        key=config.azure_key, region=config.azure_region)

    hass_interface = HAInterface(config.hass_config)

    bot = Sory(config=config, detector=detector, led=led_control,
               music=music_provider, stt=stt_provider, tts=tts_provider, hass=hass_interface, player=audio_player)

    logger.info("Sory Bot is listening.")
    stop_circulate()
    bot.detector.start(detected_callback=bot.detected_callback,
                       audio_recorder_callback=bot.audio_recorder_callback,
                       interrupt_check=interrupt_callback,
                       silent_count_threshold=6,
                       sleep_time=0.01)
