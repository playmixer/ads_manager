import logging
from logging.handlers import TimedRotatingFileHandler
import os
from config import LOGGER_LEVEL

__all__ = ['logger']

if not os.path.exists("logs/"):
    os.makedirs("logs/")

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

s_handler = logging.StreamHandler()
s_handler.setLevel(logging.DEBUG)
s_handler.setFormatter(formatter)

f_handler = TimedRotatingFileHandler(os.path.join('logs', "log.txt"), when="midnight", interval=1)
f_handler.suffix = "%Y-%m-%d"
f_handler.setLevel(logging.INFO)
f_handler.setFormatter(formatter)

logger = logging.getLogger("schedule")
logger.setLevel(LOGGER_LEVEL)
logger.addHandler(f_handler)
logger.addHandler(s_handler)
