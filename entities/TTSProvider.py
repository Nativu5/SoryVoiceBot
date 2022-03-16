import os
import time
import pyttsx3
from xml.etree import ElementTree
import requests
from utils.log import init_logging

logger = init_logging(__name__)

class _TTSProvider:
    def __init__(self):
        pass

    def text_to_speach(self,text):
        return ""
class onlineTTSProvider(_TTSProvider):
    def __init__(self):
        pass

    
    def _get_token(region, subscription_key):
        fetch_token_url = 'https://{}.api.cognitive.microsoft.com/sts/v1.0/issueToken'.format(
            region)
        headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }

        try:
            response = requests.post(fetch_token_url, headers=headers)
            response.raise_for_status()
            access_token = str(response.text)
        except Exception as e:
            logger.error("Cannot obtain access token from Azure: {}".format(e))
            raise e

        return access_token    

    def text_to_speech(self,text, key, region, fname):
        headers = {
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'sorybot'
        }

        try:
            access_token = self._get_token(region, key)
        except Exception:
            logger.warning("Change to use subscription_key directly.")
            headers["Ocp-Apim-Subscription-Key"] = key
        else:
            headers["authorization"] = "Bearer {}".format(access_token)

        url = 'https://{}.tts.speech.microsoft.com/cognitiveservices/v1'.format(
            region)

        xml_body = ElementTree.Element('speak', version='1.0')
        xml_body.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-CN')
        voice = ElementTree.SubElement(xml_body, 'voice')
        voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'zh-CN')
        voice.set('name', 'zh-CN-XiaoyanNeural')
        voice.text = text
        body = ElementTree.tostring(xml_body)

        try:
            response = requests.post(url, headers=headers, data=body)
            response.raise_for_status()
        except Exception as e:
            logger.error("Cannot obtain TTS result: ".format(e))
            raise e

        with open(fname, 'wb') as audio:
            audio.write(response.content)
        return response.content

class LocalTTSProvider(_TTSProvider):
    def __init__(self):
        pass

    def to_speach(self, text='你好'):
							engine = pyttsx3.init() # 创建对象
							rate = engine.getProperty('rate')   # 获取当前语速（默认值）
							#print (rate)                        # 打印当前语速（默认值）
							engine.setProperty('rate', 135)     # 设置一个新的语速
							volume = engine.getProperty('volume')   # 获取当前的音量 （默认值）(min=0 and max=1)
							#print (volume)                          # 打印当前音量（默认值）
							engine.setProperty('volume',1.0)    # 设置一个新的音量（0 < volume < 1）
							voices = engine.getProperty('voices')       # 获取当前的音色信息
							engine.setProperty('voice', voices[0].id)  # 改变中括号中的值,0为男性,1为女性
							engine.setProperty('voice','en')             #将音色中修改音色的语句替换
							engine.say(text)     
							engine.runAndWait()


