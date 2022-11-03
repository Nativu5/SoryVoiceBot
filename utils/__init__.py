import logging
import yaml
import os

log_level = "INFO"
logger = logging.Logger(__name__, log_level)

class Config:
    def __init__(self, path) -> None:
        self.filepath = path

    def load_all(self):
        if os.path.exists(self.filepath) == False:
            logger.critical("No config file found!")
            exit()
        with open(self.filepath, "r") as f:
            yaml_file = yaml.safe_load(f)
        try:
            self.version = yaml_file["version"]
            self.hotword = yaml_file["hotword"]
            self.hotword2 = yaml_file["hotword2"]
            self.sensitivity = yaml_file["sensitivity"]
            self.azure_key = yaml_file["azure_key"]
            self.azure_region = yaml_file["azure_region"]
            self.log_level = yaml_file["log_level"]
            self.netease_api_url = yaml_file["netease_api_url"]
            self.netease_email = yaml_file["netease_email"]
            self.netease_password_md5 = yaml_file["netease_password_md5"]
        except AttributeError:
            logger.critical("Corrupt config file!")
            exit()
        global log_level
        log_level = self.log_level

def get_config_by_name(filepath, name):
    if os.path.exists(filepath) == False:
        logger.critical("No config file found!")
        exit(-1)
    with open(filepath, "r") as f:
        yaml_file = yaml.safe_load(f)
    try:
        ret = yaml_file[name]
    except AttributeError:
        logger.critical("No such configuration.")
        exit(-1)
    return ret

def init_logging(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    log_handler = logging.StreamHandler()
    log_handler.setLevel(log_level)
    log_handler.setFormatter(logging.Formatter(
        "[%(levelname)s] %(asctime)s - %(name)s: %(message)s (%(filename)s[:%(lineno)d])"))
    logger.addHandler(log_handler)
        
    return logger
