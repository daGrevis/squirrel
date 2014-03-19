import jinja2

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()
args = helpers.get_args()


def jinja2_templating(context):
    if args.action != "generate":
        return context

    jinja2_env = (jinja2.Environment(
                  loader=jinja2.FileSystemLoader(conf["theme_dir"])))

    logger.debug("Initiating templating with Jinja2 template-language...")

    context["jinja2_env"] = jinja2_env

    return context


def inject_middlewares(middlewares):
    middlewares.add("jinja2_templating", jinja2_templating)

    return middlewares
