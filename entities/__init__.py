import os
from interface.azure import parse_wav_file, speech_to_text, text_to_speech
from interface.audio import VLCInterface
from interface.cloudmusic import CloudMusic
from interface.led import LED as _LED
from interface.qingyunke import get_reply
from utils.log import init_logging

logger = init_logging(__name__)


class Sory:
    def __init__(self, detector, led: _LED, config) -> None:
        self.detector = detector
        self.config = config
        self.LED = led
        self.VLC_instance = VLCInterface()
        self.music_provider = CloudMusic(self.config.netease_api_url)
        self.music_provider.login_by_email(
            self.config.netease_email, md5_password=self.config.netease_password_md5)
        self.is_playing = False

    def detected_callback(self):
        self.is_playing = self.VLC_instance.is_playing()
        if self.is_playing == True:
            return False
        self.VLC_instance.play_audio("resources/wozai.wav")
        self.LED.power.on()
        for i in range(0, 12):
            self.LED.switch_by_place(
                i, color={"r": 255, "g": 0, "b": 0}, bright=30)
        logger.info('Recording audio...')
        return True

    def audio_recorder_callback(self, fname):
        if self.is_playing:
            return
        logger.info("Converting audio to text")
        try:
            audio_data = parse_wav_file(fname)
            stt_text = speech_to_text(
                audio_data, self.config.azure_key, "japaneast", "zh-CN")
            logger.info("User: " + stt_text)
        except Exception as e:
            logger.warning(
                "Could not request results from STT service; {0}".format(e))
            reply = "语音转文字功能出错啦！"
        else:
            parsed_str = stt_text.split("点歌")

            self.is_playing = False
            if len(parsed_str) > 1:
                logger.info("Trying to play: " + parsed_str[1])
                song_list = self.music_provider.search_music(parsed_str[1])
                if song_list != None and len(song_list) > 0:
                    song_url = self.music_provider.get_song_url(song_list[0])
                    logger.info("Streaming {}...".format(song_url))
                    self.VLC_instance.play_audio(song_url)
                    self.is_playing = True

            if self.is_playing == False:
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
                finally:
                    os.remove("playback_" + fname)
        finally:
            os.remove(fname)

        self.LED.power.off()
