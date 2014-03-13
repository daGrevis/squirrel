#!/usr/bin/env python
import os.path as path
import importlib

import toml
import jinja2

from ware import Ware

import helpers


def get_conf():
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
        "name_for_injection_callable",
    )

    with open("conf.toml") as conf_file:
        conf = toml.loads(conf_file.read())

    for key in REQUIRED_KEYS_IN_CONF:
        if key not in conf:
            logger.error("Conf is missing key `{}`!".format(key))
            exit()

    return conf


# Inits logging.
logger = helpers.get_logger(__name__)


# Loads conf from `conf.toml`.
conf = get_conf()


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

    middlewares = plugin.inject_middlewares(middlewares)


context = {
    "is_called_from_cli": __name__ == "__main__",
    "conf": conf,
    "path_to_theme": path_to_theme,
    "jinja2_env": jinja2_env,
}
middlewares.run(context)
