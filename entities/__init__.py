from utils import init_logging
from interface.qingyunke import get_reply
from entities.STTProvider import parse_wav_file
from entities.LEDController import RED, BLUE, GREEN

logger = init_logging(__name__)

def choose_function(word_list):
    key_func_map = {'点歌' : 1, '播放': 1, '音乐': 1, "歌曲": 1, "放歌": 1, "家具": 2}
    keywords = key_func_map.keys()

    for (i, v) in enumerate(word_list):
        if v in keywords:
            return (key_func_map[v], i)
    
    return (0, 0)

class Sory:
    def __init__(self, config, detector, music, stt, tts, led, player) -> None:
        self.detector = detector
        self.config = config
        self.music = music
        self.stt = stt
        self.tts = tts
        self.led = led
        self.player = player
        self.is_playing = False

    def detected_callback(self) -> bool:
        self.is_playing = self.player.is_playing()
        if self.is_playing == True:
            logger.info('Bot is playing sounds, omitting detection...')
            return False

        self.player.play_audio("resources/wozai.wav")
        self.led.set_all_lights(RED, 30)
        logger.info('Recording audio...')
        return True

    def dectected_stop(self) -> bool:
        if self.is_playing == True:
            self.player.stop()
            self.is_playing = False
        return False

    def audio_recorder_callback(self, fname):
        stop_breathing = self.led.breathing_lights(color=RED)
        
        # 默认回复
        play_back = "resources/error.wav"

        if self.is_playing:
            return
        logger.info("Converting audio to text")

        try:
            audio_data = parse_wav_file(fname)
            stt_words = self.stt.speech_to_text(audio_data, "zh-CN")
            logger.info(f"User: {stt_words}")
        except Exception as e:
            logger.warning(f"Could not request results from STT service: {e}")
            play_back = "resources/error.wav"
        else:
            (func, idx) = choose_function(stt_words)
            self.is_playing = False

            if func == 1:
                # 放歌
                parsed_str = "".join(stt_words[idx+1:])
                logger.info(f"Trying to play: {parsed_str}")

                try:
                    song_list = self.music.search_music(parsed_str)
                    song_url = self.music.get_song_url(song_list[0]["id"])
                except:
                    # 无歌可放
                    play_back = "resources/noSong.wav"
                else:
                    logger.info(f"Streaming {song_list[0]['name']} from {song_list[0]['artists']}{song_url}...")
                    self.player.play_audio(song_url)
                    self.is_playing = True

            elif func == 2:
                # 家具
                play_back = "resources/missing.wav"

            else:
                # 即兴问答
                reply = get_reply("".join(stt_words))
                logger.info(f"Bot: {reply}")

                try:
                    self.tts.text_to_speech(reply, "playback_" + fname)
                except Exception as e:
                    logger.warning(
                        f"Could not request results from TTS service: {e}")
                    play_back = "resources/error.wav"
                else:
                    play_back = "playback_" + fname

        finally:
            if self.is_playing != True:
                self.player.play_audio(play_back)
                self.is_playing = True

        stop_breathing()
