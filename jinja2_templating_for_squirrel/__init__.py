import jinja2

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()
args = helpers.get_args()


def render_template(template_name, template_data):
    jinja2_env = (jinja2.Environment(
                  loader=jinja2.FileSystemLoader(conf["theme_dir"])))

    template = jinja2_env.get_template(template_name)
    content = template.render(**template_data)

    return content


def jinja2_templating(context):
    if args.action != "generate":
        return context

    context["render_template"] = render_template

    logger.debug("Initiating templating with Jinja2 template-language...")

    return context


def inject_middlewares(middlewares):
    middlewares.add("jinja2_templating", jinja2_templating)

    return middlewares
