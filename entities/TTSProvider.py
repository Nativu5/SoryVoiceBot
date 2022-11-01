from xml.etree import ElementTree
import requests
from utils.log import init_logging

logger = init_logging(__name__)

class AzureTTSProvider():
    def __init__(self, key, region) -> None:
        self.key = key
        self.region = region

    def _get_token(self):
        fetch_token_url = f'https://{self.region}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': self.key
        }

        try:
            response = requests.post(fetch_token_url, headers=headers)
            response.raise_for_status()
            access_token = str(response.text)
        except Exception as e:
            logger.error(f"Cannot obtain access token from Azure: {e}")
            raise e

        return access_token

    def text_to_speech(self, text, fname) -> None:
        headers = {
            'Content-Type': 'application/ssml+xml',
            'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
            'User-Agent': 'sorybot'
        }

        try:
            access_token = self._get_token()
        except Exception:
            logger.warning("Change to use subscription_key directly.")
            headers["Ocp-Apim-Subscription-Key"] = self.key
        else:
            headers["authorization"] = f"Bearer {access_token}"

        url = f'https://{self.region}.tts.speech.microsoft.com/cognitiveservices/v1'

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
            logger.error(f"Cannot obtain TTS result: {e}")
            raise e

        with open(fname, 'wb') as audio:
            audio.write(response.content)


class LocalTTSProvider():
    def __init__(self):
        pass
