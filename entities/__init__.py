from entities.switch import Switch
import os
from interface.azure import parse_wav_file, text_to_speech
from interface.audio import VLCInterface
from interface.led import LED as _LED
from interface.qingyunke import get_reply
from utils.log import init_logging
from entities.MusicProvider import CloudMusicProvider, LocalMusicProvider
from entities.STTProvider import LocalSTTProvider
logger = init_logging(__name__)


class Sory:
    def __init__(self, detector, led: _LED, config) -> None:
        self.detector = detector
        self.config = config
        self.LED = led
        self.VLC_instance = VLCInterface()
        self.music_provider = CloudMusicProvider(
            self.config.netease_api_url, None, self.config.netease_email, None, self.config.netease_password_md5)
        self.is_playing = False
        self.stt = LocalSTTProvider()

    def detected_callback(self):
        self.is_playing = self.VLC_instance.is_playing()
        if self.is_playing == True:
            return
        self.VLC_instance.play_audio("resources/wozai.wav")
        self.LED.power.on()
        for i in range(0, 12):
            self.LED.switch_by_place(
                i, color={"r": 255, "g": 0, "b": 0}, bright=30)
        logger.info('Recording audio...')
        return True
    
    def dectected_stop(self):
        if  self.is_playing == True:
            self.VLC_instance.stop()
            self.is_playing = False
        return False

    def audio_recorder_callback(self, fname):
        if self.is_playing:
            return
        logger.info("Converting audio to text")
        try:
            audio_data = parse_wav_file(fname)
            stt_text = self.stt.speech_to_text(
                audio_data)
            logger.info("User: " + stt_text)
        except Exception as e:
            logger.warning(
                "Could not request results from STT service; {0}".format(e))
            reply = "语音转文字功能出错啦！"
        else:
            func = Switch(stt_text)

            self.is_playing = False
            if func[0] == 1:
                parsed_str = stt_text.split(func[1])
                logger.info("Trying to play: " + parsed_str[1])
                song_list = self.music_provider.search_music(parsed_str[1])
                if song_list != None and len(song_list) > 0:
                    song_url = self.music_provider.get_song_url(song_list[0])
                    logger.info("Streaming {}...".format(song_url))
                    self.VLC_instance.play_audio(song_url)
                    self.is_playing = True

            if self.is_playing == False&func[0] == 0:
                reply = get_reply(stt_text)
                logger.info("Bot: " + reply)
                try:
                    play_back_data = text_to_speech(
                        reply, self.config.azure_key, "japaneast", "playback_" + fname)
                except Exception as e:
                    logger.warning(
                        "Could not request results from TTS service; {0}".format(e))
                else:
                    self.VLC_instance.play_audio("playback_" + fname)
                    self.is_playing = True

        self.LED.power.off()
