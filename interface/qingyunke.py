import requests
from utils.log import init_logging

logger = init_logging(__name__)

def get_reply(text: str):
    url = "http://api.qingyunke.com/api.php"
    params = {
        "key" : "free", 
        "appid": 0,
        "msg": text
    }

    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        r_json = resp.json()
        if r_json["result"] != 0:
            raise ValueError
        reply = r_json["content"]
    except Exception as e:
        logger.warning("Unable to fetch reply: {}".format(e))
        reply = "暂时无法理解你的话哦。"
    
    return reply