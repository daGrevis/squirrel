import os.path as path

import jinja2

import helpers


logger = helpers.get_logger(__name__)


conf = helpers.get_conf()


def jinja2_templating(context):
    path_to_theme = path.join(conf["path_to_themes"], conf["site_theme"])
    jinja2_env = jinja2.Environment(loader
                                    =jinja2.FileSystemLoader(path_to_theme))

    context["path_to_theme"] = path_to_theme
    context["jinja2_env"] = jinja2_env

    logger.debug("Initiating templating with Jinja2 template-language...")

    return context


def inject_middlewares(middlewares):
    middlewares.add("jinja2_templating", jinja2_templating)

    return middlewares
