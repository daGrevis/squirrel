import logging
import os
import os.path as path
import shutil

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()


def generate_dir(context):
    context["clean_command"](context)
    try:
        os.mkdir(conf["path_to_generated_content"])
    except FileExistsError:
        pass

    logger.debug("Creating `{}` for generated content..."
                 .format(conf["path_to_generated_content"]))


def generate_index(context):
    template = context["jinja2_env"].get_template("index.html")
    content = template.render(conf=conf,
                              pages=context["pages"])

    path_to_index_file = path.join(
        conf["path_to_generated_content"],
        conf["path_to_index_file"]
    )
    with open(path_to_index_file, "w") as index_file:
        index_file.write(content)

    logger.debug("Writing to `{}`...".format(path_to_index_file))


def generate_pages(context):
    for page in context["pages"]:
        path_to_page_dir = path.join(
            conf["path_to_generated_content"],
            page["slug"]
        )
        path_to_index_file = path.join(
            path_to_page_dir,
            conf["path_to_index_file"]
        )

        template = context["jinja2_env"].get_template("page.html")
        content = template.render(conf=conf, page=page)

        os.mkdir(path_to_page_dir)
        with open(path_to_index_file, "w") as index_file:
            index_file.write(content)

        logger.debug("Writing to `{}`...".format(path_to_index_file))


def generate_static_for_theme(context):
    path_to_theme_static = path.join(context["path_to_theme"],
                                     conf["path_to_theme_static"])
    path_to_generated_static = path.join(
        conf["path_to_generated_content"],
        conf["path_to_generated_static"]
    )

    shutil.copytree(path_to_theme_static, path_to_generated_static)

    logger.debug("Copying static from `{}` to `{}`...".
                 format(path_to_theme_static, path_to_generated_static))


def generate_command(context):
    args = helpers.get_args()

    if args.action != "generate":
        return context

    generate_dir(context)
    generate_index(context)
    generate_pages(context)
    generate_static_for_theme(context)

    message = ("Generated in `{}`!"
               .format(conf["path_to_generated_content"]))
    logger.info(message)

    return context


def inject_middlewares(middlewares):
    middlewares.add("generate_command", generate_command)

    return middlewares
