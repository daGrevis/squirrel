import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()
args = helpers.get_args()


def index_renderer(context):
    if args.action != "generate":
        return context

    virtual_fs = context.get("virtual_fs", {})

    template = context["jinja2_env"].get_template("index.html")
    content = template.render(conf=conf, pages=context["pages"])

    logger.debug("Rendering `{}`...".format(conf["index_file"]))

    virtual_fs[conf["index_file"]] = content

    logger.debug("Writing `{}` to virtual fs...".format(conf["index_file"]))

    context["virtual_fs"] = virtual_fs

    return context


def inject_middlewares(middlewares):
    middlewares.add("index_renderer", index_renderer)

    return middlewares
