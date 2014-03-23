import logging
import sys
import argparse

import toml
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


def get_args():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--conf-name", action="store", default="conf")
    arg_parser.add_argument("action")

    args = arg_parser.parse_args()

    return args


def get_conf(conf_name=None):
    if not conf_name:
        args = get_args()
        conf_name = args.conf_name

    path_to_conf_file = "{}.toml".format(conf_name)
    with open(path_to_conf_file) as conf_file:
        conf = toml.loads(conf_file.read())

    return conf
