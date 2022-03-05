'''
Logging Module
See: https://www.cnblogs.com/yyds/p/6901864.html
'''

import logging


def init_logging(level : str) -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel("DEBUG")

    log_handler = logging.StreamHandler()
    log_handler.setLevel(level)
    log_handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s: %(message)s (%(filename)s[:%(lineno)d])"))
    
    logger.addHandler(log_handler)
    return logger
