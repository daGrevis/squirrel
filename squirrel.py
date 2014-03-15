#!/usr/bin/env python
import os.path as path
import importlib
import argparse

import toml
import jinja2

from ware import Ware

import helpers


def get_conf(conf_name="conf"):
    REQUIRED_KEYS_IN_CONF = (
        "blog_title",
        "blog_description",
        "blog_theme",
        "plugins",
        "path_to_metadata_file",
        "path_to_index_file",
        "path_to_generated_content",
        "path_to_pages",
        "path_to_themes",
        "path_to_theme_static",
        "path_to_generated_static",
        "required_keys_in_page",
        "name_for_injection_callable",
    )

    path_to_conf_file = "{}.toml".format(conf_name)
    with open(path_to_conf_file) as conf_file:
        conf = toml.loads(conf_file.read())

    for key in REQUIRED_KEYS_IN_CONF:
        if key not in conf:
            logger.error("Conf is missing key `{}`!".format(key))
            exit()

    return conf


# Inits logging.
logger = helpers.get_logger(__name__)


is_called_from_cli = __name__ == "__main__"

# Inits arg-parser.
arg_parser = argparse.ArgumentParser()
if is_called_from_cli:
    arg_parser.add_argument("--conf-name", action="store", default="conf")
    arg_parser.add_argument("action")
    args = arg_parser.parse_args()
else:
    # TODO: This is kinda ugly.
    args = argparse.Namespace()
    args.conf_name = "conf"


# Loads conf from `conf.toml`.
conf = get_conf(args.conf_name)


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
    "is_called_from_cli": is_called_from_cli,
    "arg_parser": arg_parser,
    "conf": conf,
    "path_to_theme": path_to_theme,
    "jinja2_env": jinja2_env,
}
middlewares.run(context)
