#!/usr/bin/env python
import os.path as path
import importlib

from ware import Ware

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()


middlewares = Ware()
for plugin_name in conf["plugins"]:
    try:
        plugin = importlib.import_module(plugin_name)
    except ImportError:
        logger.error("Can't load plugin `{}`!".format(plugin_name))
        exit()

    middlewares = plugin.inject_middlewares(middlewares)


context = {
}
middlewares.run(context)
