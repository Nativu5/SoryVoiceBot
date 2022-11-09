from utils import init_logging
from interface.qingyunke import get_reply
from entities.STTProvider import parse_wav_file
from entities.LEDController import RED, BLUE, GREEN

logger = init_logging(__name__)

def choose_function(word_list):
    key_func_map = {'点歌' : 1, '播放': 1, '音乐': 1, "歌曲": 1, "放歌": 1, "让": 2, "把": 2, "家具": 2, "控制": 2}
    keywords = key_func_map.keys()

    for (i, v) in enumerate(word_list):
        if v in keywords:
            return (key_func_map[v], i)
    
    return (0, 0)

class Reply:
    """
    Code 0: 无需回复
    Code 1: 语音回复指定文本
    Code 2: 一般错误
    Code 3: STT 失败
    Code 4: TTS 失败
    Code 5: 未匹配歌曲
    Code 6: 未匹配设备/指令
    Code 7: 无法理解
    """
    def __init__(self, code: int, text: str = "") -> None:
        self.code = code
        self.text = text

class Sory:
    def __init__(self, config, detector, music, stt, tts, hass, led, player) -> None:
        self.detector = detector
        self.config = config
        self.music = music
        self.stt = stt
        self.tts = tts
        self.hass = hass
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

    def generate_playback(self, input_fname, reply: Reply) -> str:
        if reply.code == 0:
            return ""

        playback_fname = input_fname.replace(".wav", "_playback.wav")
        try:
            if reply.code == 1:
                self.tts.text_to_speech(reply.text, playback_fname)
            elif reply.code == 2:
                playback_fname = "resources/error.wav"
            elif reply.code == 3:
                playback_fname = "resources/error_stt.wav"
            elif reply.code == 4:
                playback_fname = "resources/error_tts.wav"
            elif reply.code == 5:
                playback_fname = "resources/missing_song.wav"
            elif reply.code == 6:
                playback_fname = "resources/missing_instruction.wav"
            elif reply.code == 7:
                playback_fname = "resources/missing_reply.wav"
        except Exception as e:
            logger.warning(f"Could not request results from TTS service: {e}")
            playback_fname = "resources/error_tts.wav"
        
        return playback_fname

    def audio_recorder_callback(self, fname):
        stop_breathing = self.led.breathing_lights(color=RED)

        if self.is_playing:
            return

        reply = Reply(0)

        # 语音识别
        logger.info("Converting audio to text")
        try:
            audio_data = parse_wav_file(fname)
            stt_words = self.stt.speech_to_text(audio_data, "zh-CN")
            logger.info(f"User: {stt_words}")
        except Exception as e:
            logger.warning(f"Could not request results from STT service: {e}")
            reply = Reply(3)
        else:
            # 语义分析
            (func, idx) = choose_function(stt_words)

            if func == 1:
                # 播放歌曲
                parsed_str = "".join(stt_words[idx+1:])
                logger.info(f"Trying to play: {parsed_str}")

                try:
                    song_list = self.music.search_music(parsed_str)
                    song_url = self.music.get_song_url(song_list[0]["id"])
                except Exception as e:
                    # 无歌可放
                    logger.warning(f"Could not request results from Music service: {e}")
                    reply = Reply(5)
                else:
                    logger.info(f"Streaming {song_list[0]['name']} from {song_list[0]['artists']}{song_url}...")
                    self.player.play_audio(song_url)
                    self.is_playing = True

            elif func == 2:
                # 家具
                try: 
                    (device_name, instruction) = self.hass.handle_device_control(stt_words[idx+1:])
                except Exception as e:
                    logger.warning(f"Error when calling HA: {e}")
                    reply = Reply(6)
                else:
                    logger.info(f"Device: {device_name}, Instruction: {instruction}")
                    reply = Reply(1, f"已对{device_name}执行了{instruction}操作。")
            else:
                # 即兴问答
                reply_text = get_reply("".join(stt_words))
                reply = Reply(1, reply_text)
                logger.info(f"Bot: {reply_text}")

        finally:
            playback_fname = self.generate_playback(fname, reply)
            if playback_fname != "":
                self.player.play_audio(playback_fname)
                self.is_playing = True
            stop_breathing()
