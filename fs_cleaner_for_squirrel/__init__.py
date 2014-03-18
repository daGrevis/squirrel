import logging
import os
import os.path as path
import shutil

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()


def clean_command():
    try:
        names = os.listdir(conf["build_dir"])
    except FileNotFoundError:
        logger.debug("Already clean!")
        return

    for name in names:
        name_path = path.join(conf["build_dir"], name)
        try:
            os.unlink(name_path)
        except IsADirectoryError:
            shutil.rmtree(name_path)

        logger.debug("Removing `{}`...".format(name_path))


def fs_cleaner(context):
    context["clean_command"] = clean_command

    args = helpers.get_args()

    if args.action != "clean":
        return context

    clean_command()

    message = ("Cleaned `{}`!"
               .format(conf["build_dir"]))
    logger.info(message)

    return context


def inject_middlewares(middlewares):
    middlewares.add("fs_cleaner", fs_cleaner)

    return middlewares
