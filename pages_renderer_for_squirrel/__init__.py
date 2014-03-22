import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()
args = helpers.get_args()


def pages_renderer(context):
    if args.action != "generate":
        return context

    render_template = context["render_template"]

    virtual_fs = context.get("virtual_fs", {})

    virtual_fs["pages"] = {}

    for page in context["pages"]:
        content = render_template("page.html", {
            "conf": conf,
            "pages": context["pages"],
            "page": page,
        })

        path_to_index_file = "pages/{}/{}".format(page["slug"],
                                                  conf["index_file"])

        logger.debug("Rendering `{}`...".format(path_to_index_file))

        virtual_fs["pages"][page["slug"]] = {}
        virtual_fs["pages"][page["slug"]][conf["index_file"]] = content

        logger.debug("Writing `{}` to virtual fs...".format(path_to_index_file))

    context["virtual_fs"] = virtual_fs

    return context


def inject_middlewares(middlewares):
    middlewares.add("pages_renderer", pages_renderer)

    return middlewares
