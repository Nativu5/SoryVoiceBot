import requests
from utils import init_logging

logger = init_logging(__name__)

class HAInterface:
    def __init__(self, config) -> None:
        self.base_url = config["url"]
        self.devices = config["devices"]

    def find_word_in_list(self, wordlist: list, keywords: list):
        for (i, word) in enumerate(wordlist):
            if word in keywords:
                return (i, word)
        return (-1, "")
    
    def handle_device_control(self, wordlist: list):
        (idx, device_name) = self.find_word_in_list(wordlist, self.devices.keys())
        if idx == -1:
            raise Exception("No device found")
        
        (idx, instruction) = self.find_word_in_list(wordlist[idx+1:], self.devices[device_name].keys())
        if idx == -1:
            raise Exception("No instruction found")

        token = self.devices[device_name][instruction]
        try:
            resp = requests.post(f"{self.base_url}/api/webhook/{token}")
            resp.raise_for_status()
        except Exception as e:
            raise e

        return (device_name, instruction)
