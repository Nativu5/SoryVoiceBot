import os
import requests
import difflib
from utils import init_logging

logger = init_logging(__name__)


class _MusicProvider:
    """
    MusicProvider Interface
    """
    def __init__(self):
        pass

    def get_music_list(self):
        pass

    def search_music(self, keyword, limit=1):
        pass

    def get_song_uri(self, id):
        pass


class CloudMusicProvider(_MusicProvider):
    """
    CloudMusic Implement of MusicProvider Interface
    """
    def __init__(self, base_url, phone=None, email=None, password=None, md5_password=None):
        super().__init__()
        self.base_url = base_url
        self.is_login = False
        self.cookie = None
        self.uid = None

        if self._load_cached_cookies() and self._check_if_login():
            logger.info("Already logged in.")
            return

        if phone != None:
            self._login_by_phone(phone, password, md5_password)
        elif email != None:
            self._login_by_email(email, password, md5_password)
        else:
            logger.warning("Insuffient infomation to log in.")
            return
    
        self._save_cookies()

    def _login_by_phone(self, phone, password=None, md5_password=None):
        url = self.base_url + "/login/cellphone"
        params = {
            "phone": phone,
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

    def _login_by_email(self, email, password=None, md5_password=None):
        url = self.base_url + "/login/email"
        params = {
            "email": email,
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
    
    def _load_cached_cookies(self) -> bool:
        if os.path.exists("netease_cookies") != True:
            return False
        with open("netease_cookies", "r") as f:
            self.cookie = f.read()
        return True

    def _save_cookies(self):
        if self.cookie == None:
            return
        with open("netease_cookies", "w") as f:
            f.write(self.cookie)
        
    def _check_if_login(self) -> bool:
        url = self.base_url + "/login/status"
    
        headers = {
            'Cookie': self.cookie
        }

        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            resp_json = resp.json()
            login_status = resp_json["data"]["account"]["status"]
        except Exception as e:
            logger.error("Fail to check login status: {}".format(e))
            self.is_login = False
            return False
        else:
            if login_status == "0":
                self.is_login = True
                return True
            else:
                return False

    def get_music_list(self):
        pass

    def search_music(self, keyword, limit=1):
        if self.is_login == False:
            return None

        url = self.base_url + "/cloudsearch"

        headers = {
            'Cookie': self.cookie
        }

        params = {
            'keywords': keyword,
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

        url = self.base_url + "/song/url"

        headers = {
            'Cookie': self.cookie
        }

        params = {
            'id': id,
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


class LocalMusicProvider(_MusicProvider):
    def __init__(self, path, media_exts=None) -> None:
        super().__init__()
        self.path = path
        self.media_exts = media_exts if media_exts != None else [
            ".wav", ".mp3", ".aac", ".m4a", ".flac", ".ogg"]

    def get_music_list(self):
        songlist = []
        for (dirpath, _, filenames) in os.walk(top=self.path):
            for i in filenames:
                if os.path.splitext(i)[-1] in self.media_exts:
                    songlist.append(os.path.join(dirpath, i))
        return songlist

    def search_music(self, keyword, limit=1):
        songlist = self.get_music_list()
        keyword = self.path + '/' + keyword
        songlist.sort(key=lambda a: difflib.SequenceMatcher(
            None, keyword, a, True).quick_ratio(), reverse=True)
        return songlist[:limit - 1]

    def get_song_uri(self, song_id):
        return song_id
