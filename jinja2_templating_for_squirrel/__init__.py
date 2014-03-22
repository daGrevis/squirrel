import jinja2

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()
args = helpers.get_args()


class TemplateRenderer(object):
    jinja2_env = None

    def render_template(self, template_name, template_data):
        if self.jinja2_env is None:
            jinja2_loader = jinja2.FileSystemLoader(conf["theme_dir"])
            self.jinja2_env = jinja2.Environment(loader=jinja2_loader)

        template = (self.jinja2_env).get_template(template_name)
        content = template.render(**template_data)

        return content


def jinja2_templating(context):
    if args.action != "generate":
        return context

    context["render_template"] = TemplateRenderer().render_template

    logger.debug("Initiating templating with Jinja2 template-language...")

    return context


def inject_middlewares(middlewares):
    middlewares.add("jinja2_templating", jinja2_templating)

    return middlewares
