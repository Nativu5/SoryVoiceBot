import requests
from utils.log import init_logging

logger = init_logging(__name__)


def get_token(region, subscription_key):
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


def recognize(audio_data, key, region, language, format="simple", profanity="masked", model_cid=None, show_all=False):
    headers = {
        "Content-type": "audio/wav; codecs=audio/pcm; samplerate=16000",
        "Accept": "application/json"
    }

    try:
        access_token = get_token(region, key)
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
        logger.error("Cannot obtain recognition result: ".format(e))
        raise e

    try:
        text = str(r_json["DisplayText"])
    except:
        raise Exception("Invalid recognition output: ".format(r_json))

    return r_json if show_all else text


if __name__ == "__main__":
    region = "japaneast"
    subscription_key = 'some_key'
    audio_data = parse_wav_file("some.wav")
    recognize(audio_data, subscription_key, region, "zh-CN")
