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


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


with open("conf.toml") as conf_file:
    conf = toml.loads(conf_file.read())


def get_dirs_for_articles():
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


def get_articles_from_dirs(dirs):
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
            logging.error("Required key is missing in metadata file!")
            exit()
        for key in conf["forbidden_keys_in_article"]:
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
    return path.join(conf["path_to_themes"], conf["blog_theme"])


def generate_articles(articles):
    for article in articles:
        dir_path = path.join(conf["path_to_generated_content"], article["slug"])
        file_path = path.join(dir_path, conf["index_file"])

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
    os.mkdir(conf["path_to_generated_content"])

    articles = get_articles()
    generate_articles(articles)

    logger.info("Generated!")


def clean():
    try:
        shutil.rmtree(conf["path_to_generated_content"])
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
