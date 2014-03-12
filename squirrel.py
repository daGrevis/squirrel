#!/usr/bin/env python
import os
import os.path as path
import logging
import shutil
import http.server as http_server
import socketserver
import importlib

import toml
import jinja2


from ware import Ware


REQUIRED_KEYS_IN_CONF = (
    "blog_title",
    "blog_description",
    "blog_theme",
    "plugins",
    "metadata_file",
    "index_file",
    "path_to_generated_content",
    "path_to_articles",
    "path_to_themes",
    "path_to_theme_static",
    "path_to_generated_static",
    "required_keys_in_article",
    "forbidden_keys_in_article",
    "server_port",
    "name_for_injection_callable",
)


# Inits logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


# Loads conf from `conf.toml`.
with open("conf.toml") as conf_file:
    conf = toml.loads(conf_file.read())

for key in REQUIRED_KEYS_IN_CONF:
    if key not in conf:
        logger.error("Conf is missing key `{}`!".format(key))
        exit()


# Inits templating.
path_to_theme = path.join(conf["path_to_themes"], conf["blog_theme"])
jinja2_loader = jinja2.FileSystemLoader(path_to_theme)
jinja2_env = jinja2.Environment(loader=jinja2_loader)


# Inits plugins.
middlewares = Ware()
for plugin_name in conf["plugins"]:
    try:
        plugin = importlib.import_module(plugin_name)
    except ImportError:
        logger.error("Can't load plugin `{}`!".format(plugin_name))
        exit()

    if not hasattr(plugin, conf["name_for_injection_callable"]):
        message = ("Plugin `{}` doesn't have `{}` callable!"
                   .format(plugin_name, conf["name_for_injection_callable"]))
        logger.error(message)
        exit()

    middlewares = plugin.inject_middlewares(middlewares)


context = {
    "is_called_from_cli": __name__ == "__main__",
    "conf": conf,
    "path_to_theme": path_to_theme,
    "jinja2_env": jinja2_env,
}
middlewares.run(context)
