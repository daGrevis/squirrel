import logging
import os
import os.path as path
import shutil

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()


def generate_command(context):
    context["clean_command"]()

    try:
        os.mkdir(conf["build_dir"])
    except FileExistsError:
        pass

    logger.debug("Creating `{}` for generated content..."
                 .format(conf["build_dir"]))


def generate_index(context):
    path_to_index_file = path.join(
        conf["build_dir"],
        conf["index_file"]
    )
    with open(path_to_index_file, "w") as index_file:
        index_file.write(context["html"]["index"])

    logger.debug("Writing to `{}`...".format(path_to_index_file))


def generate_pages(context):
    for page in context["pages"]:
        path_to_page_dir = path.join(
            conf["build_dir"],
            page["slug"]
        )
        path_to_index_file = path.join(
            path_to_page_dir,
            conf["index_file"]
        )

        os.mkdir(path_to_page_dir)
        with open(path_to_index_file, "w") as index_file:
            index_file.write(context["html"]["pages"][page["title"]])

        logger.debug("Writing to `{}`...".format(path_to_index_file))


def generate_static_for_theme(context):
    path_to_theme_static = path.join(conf["theme_dir"],
                                     conf["dir_for_build_static"])
    path_to_generated_static = path.join(
        conf["build_dir"],
        conf["dir_for_build_static"]
    )

    shutil.copytree(path_to_theme_static, path_to_generated_static)

    logger.debug("Copying static from `{}` to `{}`...".
                 format(path_to_theme_static, path_to_generated_static))


def fs_writer(context):
    context["generate_command"] = generate_command

    args = helpers.get_args()

    if args.action != "generate":
        return context

    generate_command(context)
    generate_index(context)
    generate_pages(context)
    generate_static_for_theme(context)

    message = ("Generated in `{}`!"
               .format(conf["build_dir"]))
    logger.info(message)

    return context


def inject_middlewares(middlewares):
    middlewares.add("fs_writer", fs_writer)

    return middlewares
