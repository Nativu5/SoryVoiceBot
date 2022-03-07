'''
Logging Module
See: https://www.cnblogs.com/yyds/p/6901864.html
'''

import logging
from . import config


def init_logging(name: str) -> logging.Logger:
    level = config.Config("config.yaml").get_config_by_name("log_level")

    logger = logging.getLogger(name)
    logger.setLevel(level)

    log_handler = logging.StreamHandler()
    log_handler.setLevel(level)
    log_handler.setFormatter(logging.Formatter(
        "[%(levelname)s] %(asctime)s: %(message)s (%(filename)s[:%(lineno)d])"))

    logger.addHandler(log_handler)
    return logger
