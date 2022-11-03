import wave
from io import BytesIO
import requests
from utils import init_logging
from vosk import Model, KaldiRecognizer
import json

logger = init_logging(__name__)


def parse_wav_file(fname):
    try:
        with open(fname, "rb") as fo:
            raw = fo.read()
    except FileNotFoundError as e:
        logger.error(f"Cannot open recorded wav file: {e}")
        raise e
    return raw


class LocalSTTProvider():
    def __init__(self, model) -> None:
        self.model = model

    def speech_to_text(self, audio_data) -> list[str]:
        model = Model(model_path=self.model)
        rec = KaldiRecognizer(model, 16000)
        rec.SetWords(True)
        rec.AcceptWaveform(audio_data)
        resp_json = json.loads(rec.FinalResult())
        return resp_json['text'].split(' ')


class AzureSTTProvider():
    def __init__(self, key, region) -> None:
        self.key = key
        self.region = region

    def _generate_wav(self, data):
        byte_buf = BytesIO()
        with wave.open(byte_buf, 'wb') as fo:
            fo.setnchannels(1)
            fo.setsampwidth(2)
            fo.setframerate(16000)
            fo.writeframes(data)
        return byte_buf

    def _get_token(self):
        fetch_token_url = f'https://{self.region}.api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {
            'Ocp-Apim-Subscription-Key': self.key
        }

        try:
            response = requests.post(
                fetch_token_url, headers=headers)  # type: ignore
            response.raise_for_status()
            access_token = str(response.text)
        except Exception as e:
            logger.error(f"Cannot obtain access token from Azure: {e}")
            raise e

        return access_token

    def speech_to_text(self, audio_data, language="zh-CN", profanity="masked", model_cid=None) -> list[str]:
        headers = {
            "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
            "Accept": "application/json"
        }

        try:
            access_token = self._get_token()
        except Exception:
            logger.warning("Change to use subscription_key directly.")
            headers["Ocp-Apim-Subscription-Key"] = self.key
        else:
            headers["authorization"] = f"Bearer {access_token}"

        recognize_url = f'https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1'

        params = {
            "language": language,
            "format": "detailed",
            "profanity": profanity
        }
        if model_cid is not None:
            params["cid"] = model_cid

        try:
            response = requests.post(
                recognize_url, headers=headers, params=params, data=audio_data)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            
            r_json = response.json()
            if r_json["RecognitionStatus"] != "Success":
                raise Exception(f"Invalid STT output {r_json}")
            
            lexical_text = str(r_json["NBest"][0]["Lexical"])
        except Exception as e:
            logger.error(f"Cannot obtain STT result: {e}")
            raise e

        return lexical_text.split(' ')
