import logging
import os
import os.path as path
import fnmatch
import glob

import toml

import helpers


logger = helpers.get_logger(__name__)


def get_dirs_for_pages(conf):
    dirs = []

    for root, _, files in os.walk(conf["path_to_pages"]):
        for file_path in fnmatch.filter(files, conf["path_to_metadata_file"]):
            dir = path.dirname(path.join(root, file_path))
            dirs.append(dir)

    return dirs


def get_pages_from_dirs(conf, dirs):
    pages = []
    for dir in dirs:
        page = {}

        path_to_metadata_file = path.join(dir, conf["path_to_metadata_file"])
        with open(path_to_metadata_file) as metadata_file:
            page = toml.loads(metadata_file.read())

        try:
            for key in conf["required_keys_in_page"]:
                page[key]
        except KeyError:
            message = "`{}` key is missing from metadata file!".format(key)
            logger.error(message)
            exit()

        content_path = path.join(dir, page["content_path"])
        content_path = glob.glob(content_path)
        if len(content_path) != 1:
            logger.error("Content path matched less or more than needed!")
            exit()
        content_path = content_path[0]

        with open(content_path) as content_file:
            page["content"] = content_file.read()

        pages.append(page)

    return pages


def filesystem_loader(context):
    conf = context["conf"]

    dirs = get_dirs_for_pages(conf)
    pages = get_pages_from_dirs(conf, dirs)

    context["pages"] = pages

    return context


def inject_middlewares(middlewares):
    middlewares.add("filesystem_loader", filesystem_loader)

    return middlewares
