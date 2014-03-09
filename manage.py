import os
import os.path as path
import logging
import argparse
import shutil
import fnmatch
import glob

import toml
import markdown


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


PATH_TO_GENERATED_CONTENT = "generated_content/"
PATH_TO_ARTICLES = "articles/"
REQUIRED_KEYS_IN_METADATA = ("title", "created", "content_path")


def get_dirs_for_articles():
    """
    Gets directories that are valid articles. Valid is any directory that
    contains `metadata.toml` file and lives under `PATH_TO_ARTICLES` constant.
    """

    dirs = []

    for root, _, files in os.walk(PATH_TO_ARTICLES):
        for file_path in fnmatch.filter(files, "metadata.toml"):
            dir = path.dirname(path.join(root, file_path))
            dirs.append(dir)

    return dirs


def get_articles_from_dirs(dirs):
    """
    Gets articles from article directories. Returns list of dictionaries with
    metadata and content.
    """

    articles = []
    for dir in dirs:
        article = {}

        with open(path.join(dir, "metadata.toml")) as metadata_file:
            article["metadata"] = toml.loads(metadata_file.read())

        try:
            for key in REQUIRED_KEYS_IN_METADATA:
                article["metadata"][key]
        except KeyError:
            logging.error("Required key is missing in metadata file!")
            exit()

        content_path = path.join(dir, article["metadata"]["content_path"])
        content_path = glob.glob(content_path)
        if len(content_path) != 1:
            logging.error("Content path matched less or more than needed!")
            exit()
        content_path = content_path[0]

        with open(content_path) as content_file:
            article["content"] = content_file.read()

        articles.append(article)

    return articles


def get_articles_in_descending_order(articles):
    articles = sorted(articles, key=lambda x: x["metadata"]["created"],
                      reverse=True)
    return articles


def get_articles():
    dirs = get_dirs_for_articles()

    articles = get_articles_from_dirs(dirs)
    articles = get_articles_in_descending_order(articles)

    return articles


def generate():
    clean()  # TODO: Re-think what should happen when dir is not empty.
    os.mkdir(PATH_TO_GENERATED_CONTENT)

    articles = get_articles()

    for article in articles:
        dir_path = path.join(PATH_TO_GENERATED_CONTENT,
                             article["metadata"]["slug"])
        file_path = path.join(dir_path, "index.html")

        parsed_content = markdown.markdown(article["content"])

        os.mkdir(dir_path)
        with open(file_path, "w") as index_file:
            index_file.write(parsed_content)

    logger.info("Generated!")


def clean():
    try:
        shutil.rmtree(PATH_TO_GENERATED_CONTENT)
        logger.info("Cleaned!")
    except FileNotFoundError:
        logger.info("Clean already!")


parser = argparse.ArgumentParser()

parser.add_argument("action")

args = parser.parse_args()

if args.action == "generate":
    generate()
elif args.action == "clean":
    clean()
else:
    exit("Unknow action!")
