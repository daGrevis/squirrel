import logging
import os
import os.path as path
import fnmatch
import glob

import toml

import helpers


logger = helpers.get_logger(__name__)


def get_dirs_for_articles(conf):
    """
    Gets directories that are valid articles. Valid is any directory that
    contains `metadata.toml` file and lives under `PATH_TO_ARTICLES` constant.
    """

    dirs = []

    for root, _, files in os.walk(conf["path_to_articles"]):
        for file_path in fnmatch.filter(files, conf["metadata_file"]):
            dir = path.dirname(path.join(root, file_path))
            dirs.append(dir)

    return dirs


def get_articles_from_dirs(conf, dirs):
    """
    Gets articles from article directories. Returns list of dictionaries with
    metadata and content.
    """

    articles = []
    for dir in dirs:
        article = {}

        with open(path.join(dir, conf["metadata_file"])) as metadata_file:
            article = toml.loads(metadata_file.read())

        try:
            for key in conf["required_keys_in_article"]:
                article[key]
        except KeyError:
            message = "`{}` key is missing from metadata file!".format(key)
            logger.error(message)
            exit()
        for key in conf["forbidden_keys_in_article"]:
            if key in article:
                logger.error("Forbidden key is in metadata file!")
                exit()

        content_path = path.join(dir, article["content_path"])
        content_path = glob.glob(content_path)
        if len(content_path) != 1:
            logger.error("Content path matched less or more than needed!")
            exit()
        content_path = content_path[0]

        with open(content_path) as content_file:
            article["raw_content"] = content_file.read()

        articles.append(article)

    return articles


def filesystem_loader(context):
    conf = context["conf"]

    dirs = get_dirs_for_articles(conf)
    articles = get_articles_from_dirs(conf, dirs)

    context["articles"] = articles

    return context


def inject_middlewares(middlewares):
    middlewares.add("filesystem_loader", filesystem_loader)

    return middlewares
