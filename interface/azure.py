from xml.etree import ElementTree
import requests
from utils.log import init_logging

logger = init_logging(__name__)


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


def parse_wav_file(fname):
    try:
        with open(fname, "rb") as fo:
            raw = fo.read()
    except FileNotFoundError as e:
        logger.error("Cannot open recorded wav file: {}".format(e))
        raise e
    return raw


def speech_to_text(audio_data, key, region, language, format="simple", profanity="masked", model_cid=None, show_all=False):
    headers = {
        "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }

    try:
        access_token = _get_token(region, key)
    except Exception:
        logger.warning("Change to use subscription_key directly.")
        headers["Ocp-Apim-Subscription-Key"] = key
    else:
        headers["authorization"] = "Bearer {}".format(access_token)

    recognize_url = 'https://{}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1'.format(
        region)

    params = {
        "language": language,
        "format": format,
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
    except Exception as e:
        logger.error("Cannot obtain STT result: ".format(e))
        raise e

    try:
        text = str(r_json["DisplayText"])
    except:
        raise Exception("Invalid STT output: ".format(r_json))

    return r_json if show_all else text


def text_to_speech(text, key, region, fname):
    headers = {
        'Content-Type': 'application/ssml+xml',
        'X-Microsoft-OutputFormat': 'riff-24khz-16bit-mono-pcm',
        'User-Agent': 'sorybot'
    }

    try:
        access_token = _get_token(region, key)
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


def _get_voices_list(access_token, region):
    url = f'https://{region}.tts.speech.microsoft.com/cognitiveservices/voices/list'
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("\nAvailable voices: \n" + response.text)
    except Exception as e:
        print("Something went wrong: {}".format(e))


if __name__ == "__main__":
    region = "japaneast"
    subscription_key = 'some_key'
    # audio_data = parse_wav_file("some.wav")
    # speech_to_text(audio_data, subscription_key, region, "zh-CN")
    text_to_speech("我在！", key=subscription_key,
                   region=region, fname="sample.wav")
