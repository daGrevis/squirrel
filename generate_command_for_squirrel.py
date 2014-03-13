import logging
import os
import os.path as path
import shutil
import argparse

import helpers


logger = helpers.get_logger(__name__)


def generate_dir(context):
    # TODO: Re-think what should happen when dir is not empty.
    context["clean_command"](context)
    try:
        os.mkdir(context["conf"]["path_to_generated_content"])
    except FileExistsError:
        pass


def generate_static_for_theme(context):
    path_to_theme_static = path.join(context["path_to_theme"],
                                     context["conf"]["path_to_theme_static"])
    path_to_generated_static = path.join(
        context["conf"]["path_to_generated_content"],
        context["conf"]["path_to_generated_static"]
    )

    shutil.copytree(path_to_theme_static, path_to_generated_static)


def generate_index(context):
    template = context["jinja2_env"].get_template("index.html")
    content = template.render(conf=context["conf"],
                              articles=context["articles"])

    path_to_index_file = path.join(
        context["conf"]["path_to_generated_content"],
        context["conf"]["path_to_index_file"]
    )
    with open(path_to_index_file, "w") as index_file:
        index_file.write(content)


def generate_articles(context):
    for article in context["articles"]:
        path_to_article_dir = path.join(
            context["conf"]["path_to_generated_content"],
            article["slug"]
        )
        path_to_index_file = path.join(
            path_to_article_dir,
            context["conf"]["path_to_index_file"]
        )

        template = context["jinja2_env"].get_template("article.html")
        content = template.render(conf=context["conf"], article=article)

        os.mkdir(path_to_article_dir)
        with open(path_to_index_file, "w") as index_file:
            index_file.write(content)


def generate_command(context):
    if context["is_called_from_cli"]:
        arg_parser = context["arg_parser"]
        args = arg_parser.parse_args()

        if args.action == "generate":
            generate_dir(context)
            generate_static_for_theme(context)
            generate_index(context)
            generate_articles(context)

            message = ("Generated in `{}`!"
                       .format(context["conf"]["path_to_generated_content"]))
            logger.info(message)

    return context


def inject_middlewares(middlewares):
    middlewares.add("generate_command", generate_command)

    return middlewares
