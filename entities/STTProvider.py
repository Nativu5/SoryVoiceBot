import wave
from io import BytesIO
import requests
from utils.log import init_logging
from vosk import Model, KaldiRecognizer
import json

logger = init_logging(__name__)


class _STTProvider:
    def __init__(self):
        pass

    def speech_to_text(self):
        return ""


class LocalSTTProvider(_STTProvider):
    def __init__(self) -> None:
        pass

    def speech_to_text(self, audio_data, show_all=False) -> str:
        # model = Model("resources/vosk_model")
        model = Model("resources/vosk-model-small-cn-0.3")
        rec = KaldiRecognizer(model, 16000)
        rec.SetWords(True)
        rec.AcceptWaveform(audio_data)
        if show_all == True:
            return rec.FinalResult()
        resp_json = json.loads(rec.FinalResult())
        print(resp_json)
        return resp_json["text"]


class AzureSTTProvider(_STTProvider):
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
        fetch_token_url = 'https://{}.api.cognitive.microsoft.com/sts/v1.0/issueToken'.format(
            self.region)
        headers = {
            'Ocp-Apim-Subscription-Key': self.key
        }

        try:
            response = requests.post(fetch_token_url, headers=headers)
            response.raise_for_status()
            access_token = str(response.text)
        except Exception as e:
            logger.error("Cannot obtain access token from Azure: {}".format(e))
            raise e

        return access_token

    def speech_to_text(self, audio_data, language, format="simple", profanity="masked", model_cid=None, show_all=False):
        wav_data = self._generate_wav(audio_data)

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
            headers["authorization"] = "Bearer {}".format(access_token)

        recognize_url = 'https://{}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1'.format(
            self.region)

        params = {
            "language": language,
            "format": format,
            "profanity": profanity
        }
        if model_cid is not None:
            params["cid"] = model_cid

        try:
            response = requests.post(
                recognize_url, headers=headers, params=params, data=wav_data)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            r_json = response.json()
        except Exception as e:
            logger.error("Cannot obtain STT result: ".format(e))
            raise e

        try:
            text = str(r_json["DisplayText"])
        except:
            raise Exception("Invalid STT output: ".format(r_json))

        return r_json if show_all else text
