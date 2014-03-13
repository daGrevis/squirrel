import logging
import sys

from clint.textui import colored


TYPES_TO_COLOR_CALLABLES = {
    "CRITICAL": colored.magenta,
    "ERROR": colored.red,
    "WARNING": colored.yellow,
    "INFO": colored.green,
    "DEBUG": colored.blue,
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg):
        super().__init__(msg)

    def format(self, record):
        color_callable = TYPES_TO_COLOR_CALLABLES[record.levelname]
        record.msg = color_callable(record.msg)
        return super().format(record)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = ColoredFormatter("%(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
