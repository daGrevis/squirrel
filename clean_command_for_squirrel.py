import logging
import os
import os.path as path
import shutil
import argparse


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def clean_dir(context):
    try:
        names = os.listdir(context["conf"]["path_to_generated_content"])
    except FileNotFoundError:
        logger.info("Already clean!")
        return

    for name in names:
        name_path = path.join(context["conf"]["path_to_generated_content"], name)
        try:
            os.unlink(name_path)
        except IsADirectoryError:
            shutil.rmtree(name_path)


def clean_command(context):
    if context["is_called_from_cli"]:
        arg_parser = argparse.ArgumentParser()

        arg_parser.add_argument("action")

        args = arg_parser.parse_args()

        if args.action == "clean":
            clean_dir(context)

            logger.info("Cleaned!")

    context["clean_command"] = clean_dir

    return context


def inject_middlewares(middlewares):
    middlewares.add("clean_command", clean_command)

    return middlewares
