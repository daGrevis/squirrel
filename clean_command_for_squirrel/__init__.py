import logging
import os
import os.path as path
import shutil

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()


def clean_dir(context):
    try:
        names = os.listdir(conf["path_to_generated_content"])
    except FileNotFoundError:
        logger.debug("Already clean!")
        return

    for name in names:
        name_path = path.join(conf["path_to_generated_content"], name)
        try:
            os.unlink(name_path)
        except IsADirectoryError:
            shutil.rmtree(name_path)

        logger.debug("Removing `{}`...".format(name_path))


def clean_command(context):
    context["clean_command"] = clean_dir

    args = helpers.get_args()

    if args.action != "clean":
        return context

    clean_dir(context)

    message = ("Cleaned `{}`!"
               .format(conf["path_to_generated_content"]))
    logger.info(message)

    return context


def inject_middlewares(middlewares):
    middlewares.add("clean_command", clean_command)

    return middlewares
