import os
import os.path as path
import fnmatch
import glob

import toml

import helpers


logger = helpers.get_logger(__name__)


conf = helpers.get_conf()


def get_dirs_for_pages():
    dirs = []

    for root, _, files in os.walk(conf["source_dir"]):
        for file_path in fnmatch.filter(files, conf["metadata_file"]):
            dir = path.dirname(path.join(root, file_path))
            dirs.append(dir)

            logger.debug("Loading `{}` from `{}`..."
                         .format(dir, conf["source_dir"]))

    return dirs


def get_pages_from_dirs(dirs):
    pages = []
    for dir in dirs:
        page = {}

        path_to_metadata_file = path.join(dir, conf["metadata_file"])
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


def fs_reader(context):
    args = helpers.get_args()

    if args.action != "generate":
        return context

    dirs = get_dirs_for_pages()
    pages = get_pages_from_dirs(dirs)

    context["pages"] = pages

    return context


def inject_middlewares(middlewares):
    middlewares.add("fs_reader", fs_reader)

    return middlewares
