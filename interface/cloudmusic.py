import requests
from utils.log import init_logging

logger = init_logging(__name__)

class CloudMusic:
    def __init__(self, base_url):
        self.base_url = base_url
        self.is_login = False
        self.cookie = None
        self.uid = None

    def login_by_phone(self, phone, password=None, md5_password=None):
        url = self.base_url + "/login/cellphone"
        params = {
            "phone" : phone,
        }
        
        if md5_password != None:
            params["md5_password"] = md5_password
        elif password != None:
            params["password"] = password
        else:
            logger.error("Too few arguments are given.")
            return False

        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            resp_json = resp.json()
            cookie = resp_json["cookie"]
            uid = resp_json["account"]["id"]
        except Exception as e:
            logger.error("Fail to login to CloudMusic by phone: {}".format(e))
            self.is_login = False
            return False
        else:
            self.is_login = True

        self.cookie = cookie
        self.uid = uid
        return True
    
    def login_by_email(self, email, password=None, md5_password=None):
        url = self.base_url + "/login/email"
        params = {
            "email" : email,
        }
        
        if md5_password != None:
            params["md5_password"] = md5_password
        elif password != None:
            params["password"] = password
        else:
            logger.error("Too few arguments are given.")
            return False

        try:
            resp = requests.get(url, params=params)
            resp.raise_for_status()
            resp_json = resp.json()
            cookie = resp_json["cookie"]
            uid = resp_json["account"]["id"]
        except Exception as e:
            logger.error("Fail to login to CloudMusic by email: {}".format(e))
            self.is_login = False
            return False
        else:
            self.is_login = True

        self.cookie = cookie
        self.uid = uid
        return True

    def get_nickname(self):
        url = self.base_url + "/login/status"

        try:
            resp = requests.get(url)
            resp.raise_for_status()
            resp_json = resp.json()
            nickname = resp_json["data"]["profile"]["nickname"]
        except Exception as e:
            logger.error("Fail to check login status: {}".format(e))
            self.is_login = False
            nickname = None
        else:
            self.is_login = True
        
        return nickname

    def get_music_list(self):
        pass

    def search_music(self, keyword, limit=1):
        if self.is_login == False:
            return None

        url = self.base_url +  "/cloudsearch"

        headers = {
            'Cookie': self.cookie
        }

        params = {
            'keywords' : keyword,
            'limit': limit
        }

        songlist = []
        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            resp_json = resp.json()
            assert isinstance(resp_json["result"]["songs"], list)
            for song in resp_json["result"]["songs"]:
                songlist.append(song["id"])
            assert isinstance(songlist, list)
        except Exception as e:
            logger.error("Fail to search: {}".format(e))
            return None
        
        return songlist

    def get_song_url(self, id, br=320000):
        if self.is_login == False:
            return None

        url = self.base_url +  "/song/url"

        headers = {
            'Cookie': self.cookie
        }

        params = {
            'id' : id,
            'br': br
        }

        try:
            resp = requests.get(url, headers=headers, params=params)
            resp.raise_for_status()
            resp_json = resp.json()
            play_url = resp_json["data"][0]["url"]
        except Exception as e:
            logger.error("Fail to get url for stream: {}".format(e))
            return None
        
        return play_url
        

if __name__ == "__main__":
    import logging
    logger = logging.getLogger(__name__)

    music_provider = CloudMusic("http://localhost:3000")
    music_provider.login_by_email("sdtalyk@163.com", md5_password="8c97677e7cf25c075d5a0f8c907daaca")
    
    songlist = music_provider.search_music("海阔天空", 1)
    print(songlist)
    assert isinstance(songlist, list)

    play_url = music_provider.get_song_url(songlist[0])
    print(play_url)
    