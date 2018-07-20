import logging
import os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))


def get_logger(name):
    logger = logging.getLogger(name)
    return logger
