import os
import os.path as path
import logging
import argparse
import shutil
import fnmatch
import glob

import toml
import markdown
import jinja2

import conf


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def get_dirs_for_articles():
    """
    Gets directories that are valid articles. Valid is any directory that
    contains `metadata.toml` file and lives under `PATH_TO_ARTICLES` constant.
    """

    dirs = []

    for root, _, files in os.walk(conf.PATH_TO_ARTICLES):
        for file_path in fnmatch.filter(files, conf.METADATA_FILE):
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

        with open(path.join(dir, conf.METADATA_FILE)) as metadata_file:
            article = toml.loads(metadata_file.read())

        try:
            for key in conf.REQUIRED_KEYS_IN_ARTICLE:
                article[key]
        except KeyError:
            logging.error("Required key is missing in metadata file!")
            exit()
        for key in conf.FORBIDDEN_KEYS_IN_ARTICLE:
            if key in article:
                logging.error("Forbidden key is in metadata file!")
                exit()

        content_path = path.join(dir, article["content_path"])
        content_path = glob.glob(content_path)
        if len(content_path) != 1:
            logging.error("Content path matched less or more than needed!")
            exit()
        content_path = content_path[0]

        with open(content_path) as content_file:
            article["raw_content"] = content_file.read()

        articles.append(article)

    return articles


def get_articles():
    dirs = get_dirs_for_articles()

    articles = get_articles_from_dirs(dirs)

    return articles


def get_path_to_theme():
    return path.join(conf.PATH_TO_THEMES, conf.THEME)


def generate_articles(articles):
    for article in articles:
        dir_path = path.join(conf.PATH_TO_GENERATED_CONTENT, article["slug"])
        file_path = path.join(dir_path, conf.INDEX_FILE)

        article["content"] = markdown.markdown(article["raw_content"])

        path_to_theme = get_path_to_theme()
        jinja2_loader = jinja2.FileSystemLoader(path_to_theme)
        jinja2_env = jinja2.Environment(loader=jinja2_loader)
        template = jinja2_env.get_template("article.html")
        content = template.render(conf=conf, article=article)

        os.mkdir(dir_path)
        with open(file_path, "w") as index_file:
            index_file.write(content)


def generate():
    clean()  # TODO: Re-think what should happen when dir is not empty.
    os.mkdir(conf.PATH_TO_GENERATED_CONTENT)

    articles = get_articles()
    generate_articles(articles)

    logger.info("Generated!")


def clean():
    try:
        shutil.rmtree(conf.PATH_TO_GENERATED_CONTENT)
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
