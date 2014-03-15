import logging
import os
import os.path as path
import shutil
import argparse

import helpers


logger = helpers.get_logger(__name__)


def generate_dir(context):
    context["clean_command"](context)
    try:
        os.mkdir(context["conf"]["path_to_generated_content"])
    except FileExistsError:
        pass

    logger.debug("Creating `{}` for generated content..."
                 .format(context["conf"]["path_to_generated_content"]))


def generate_index(context):
    template = context["jinja2_env"].get_template("index.html")
    content = template.render(conf=context["conf"],
                              pages=context["pages"])

    path_to_index_file = path.join(
        context["conf"]["path_to_generated_content"],
        context["conf"]["path_to_index_file"]
    )
    with open(path_to_index_file, "w") as index_file:
        index_file.write(content)

    logger.debug("Writing to `{}`...".format(path_to_index_file))


def generate_pages(context):
    for page in context["pages"]:
        path_to_page_dir = path.join(
            context["conf"]["path_to_generated_content"],
            page["slug"]
        )
        path_to_index_file = path.join(
            path_to_page_dir,
            context["conf"]["path_to_index_file"]
        )

        template = context["jinja2_env"].get_template("page.html")
        content = template.render(conf=context["conf"], page=page)

        os.mkdir(path_to_page_dir)
        with open(path_to_index_file, "w") as index_file:
            index_file.write(content)

        logger.debug("Writing to `{}`...".format(path_to_index_file))


def generate_static_for_theme(context):
    path_to_theme_static = path.join(context["path_to_theme"],
                                     context["conf"]["path_to_theme_static"])
    path_to_generated_static = path.join(
        context["conf"]["path_to_generated_content"],
        context["conf"]["path_to_generated_static"]
    )

    shutil.copytree(path_to_theme_static, path_to_generated_static)

    logger.debug("Copying static from `{}` to `{}`...".
                 format(path_to_theme_static, path_to_generated_static))


def generate_command(context):
    if context["is_called_from_cli"]:
        arg_parser = context["arg_parser"]
        args = arg_parser.parse_args()

        if args.action == "generate":
            generate_dir(context)
            generate_index(context)
            generate_pages(context)
            generate_static_for_theme(context)

            message = ("Generated in `{}`!"
                       .format(context["conf"]["path_to_generated_content"]))
            logger.info(message)

    return context


def inject_middlewares(middlewares):
    middlewares.add("generate_command", generate_command)

    return middlewares
