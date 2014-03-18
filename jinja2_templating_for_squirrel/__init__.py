import os.path as path

import jinja2

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()


def jinja2_templating(context):
    args = helpers.get_args()

    if args.action != "generate":
        return context

    jinja2_env = (jinja2.Environment(
                  loader=jinja2.FileSystemLoader(conf["theme_dir"])))

    logger.debug("Initiating templating with Jinja2 template-language...")

    html = {}

    index_template = jinja2_env.get_template("index.html")
    html["index"] = index_template.render(conf=conf, pages=context["pages"])

    logger.debug("Rendering `index.html` with Jinja2...")

    html["pages"] = {}

    for page in context["pages"]:
        title = page["title"]

        page_template = jinja2_env.get_template("page.html")
        html["pages"][title] = page_template.render(conf=conf, page=page)

        logger.debug("Rendering `page.html` with Jinja2 for `{}` page..."
                     .format(title))

    context["jinja2_env"] = jinja2_env
    context["html"] = html

    return context


def inject_middlewares(middlewares):
    middlewares.add("jinja2_templating", jinja2_templating)

    return middlewares
