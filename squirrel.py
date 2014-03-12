#!/usr/bin/env python
import os
import os.path as path
import logging
import argparse
import shutil
import fnmatch
import glob
import http.server as http_server
import socketserver

import toml
import markdown
import jinja2


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class MiddlewareDuplicationError(Exception):
    def __init__(self, middleware_name, middleware_names):
        message = ("Middleware `{}` was already found in `{}` middlewares!"
                   .format(middleware_name, middleware_names))
        super().__init__(message)


class MiddlewareMissingError(Exception):
    def __init__(self, middleware_name, middleware_names):
        message = ("Middleware `{}` wasn't found between `{}` middlewares!"
                   .format(middleware_name, middleware_names))
        super().__init__(message)


class MiddlewareOrderError(Exception):
    def __init__(self, middleware_name,
                 names_for_before_middlewares, names_for_after_middlewares):
        message = ("Middleware `{}` can't be added before `{}` middlewares"
                    " and after `{}` middlewares!"
                   .format(middleware_name,
                           names_for_before_middlewares,
                           names_for_after_middlewares))
        super().__init__(message)


class Ware(object):
    def __init__(self, middlewares=[]):
        self.middlewares = []

    def get_names_for_middlewares(self):
        return [name for name, _ in self.middlewares]

    def add(self, middleware_name, middleware_callable,
            names_for_before_middlewares=[], names_for_after_middlewares=[]):

        names_for_middlewares = self.get_names_for_middlewares()

        if middleware_name in names_for_middlewares:
            raise MiddlewareDuplicationError(middleware_name,
                                             names_for_middlewares)

        if not names_for_before_middlewares and not names_for_after_middlewares:
            (self.middlewares).append((middleware_name, middleware_callable, ))
            return

        for name in names_for_before_middlewares:
            if name not in names_for_middlewares:
                raise MiddlewareMissingError(name, names_for_middlewares)

        for name in names_for_after_middlewares:
            if name not in names_for_middlewares:
                raise MiddlewareMissingError(name, names_for_middlewares)

        if names_for_before_middlewares and not names_for_after_middlewares:
            (self.middlewares).append((middleware_name, middleware_callable, ))
            return

        if not names_for_before_middlewares and names_for_after_middlewares:
            (self.middlewares).insert(0,
                                      (middleware_name, middleware_callable, ))
            return

        if names_for_before_middlewares and names_for_after_middlewares:

            max_index_for_before_middlewares = 0
            for name in names_for_before_middlewares:
                i = names_for_middlewares.index(name)
                if i > max_index_for_before_middlewares:
                    max_index_for_before_middlewares = i

            min_index_for_after_middlewares = len(names_for_middlewares)
            for name in names_for_after_middlewares:
                i = names_for_middlewares.index(name)
                if i < min_index_for_after_middlewares:
                    min_index_for_after_middlewares = i

            if (max_index_for_before_middlewares
                >= min_index_for_after_middlewares):
                raise MiddlewareOrderError(middleware_name,
                                           names_for_before_middlewares,
                                           names_for_after_middlewares)

            (self.middlewares).insert(min_index_for_after_middlewares,
                                      (middleware_name, middleware_callable, ))
            return

    def remove(self, middleware_name):
        names_for_middlewares = self.get_names_for_middlewares()

        if middleware_name not in names_for_middlewares:
            raise MiddlewareMissingError(middleware_name, names_for_middlewares)

        for i, (name, _) in enumerate(self.middlewares):
            if name == middleware_name:
                (self.middlewares).pop(i)
                break

    def run(self):
        for _, middleware_callable in self.middlewares:
            middleware_callable()


# Loads conf from conf.toml.
with open("conf.toml") as conf_file:
    conf = toml.loads(conf_file.read())


# Inits templating.
path_to_theme = path.join(conf["path_to_themes"], conf["blog_theme"])
jinja2_loader = jinja2.FileSystemLoader(path_to_theme)
jinja2_env = jinja2.Environment(loader=jinja2_loader)


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

        article["content"] = markdown.markdown(article["raw_content"])

        articles.append(article)

    return articles


def generate_static_for_theme():
    path_to_theme_static = path.join(path_to_theme,
                                     conf["path_to_theme_static"])
    path_to_generated_static = path.join(conf["path_to_generated_content"],
                                         conf["path_to_generated_static"])

    shutil.copytree(path_to_theme_static, path_to_generated_static)


def generate_index(articles):
    template = jinja2_env.get_template("index.html")
    content = template.render(conf=conf, articles=articles)

    path_to_index_file = path.join(conf["path_to_generated_content"],
                                   conf["index_file"])
    with open(path_to_index_file, "w") as index_file:
        index_file.write(content)


def generate_articles(articles):
    for article in articles:
        path_to_article_dir = path.join(conf["path_to_generated_content"],
                                        article["slug"])
        path_to_index_file = path.join(path_to_article_dir, conf["index_file"])

        template = jinja2_env.get_template("article.html")
        content = template.render(conf=conf, article=article)

        os.mkdir(path_to_article_dir)
        with open(path_to_index_file, "w") as index_file:
            index_file.write(content)


def generate():
    clean()  # TODO: Re-think what should happen when dir is not empty.
    try:
        os.mkdir(conf["path_to_generated_content"])
    except FileExistsError:
        pass

    dirs = get_dirs_for_articles()
    articles = get_articles_from_dirs(dirs)

    generate_static_for_theme()
    generate_index(articles)
    generate_articles(articles)

    logger.info("Generated!")


def clean():
    try:
        names = os.listdir(conf["path_to_generated_content"])
    except FileNotFoundError:
        logger.info("Already clean!")
        return

    for name in names:
        name_path = path.join(conf["path_to_generated_content"], name)
        try:
            os.unlink(name_path)
        except IsADirectoryError:
            shutil.rmtree(name_path)

    logger.info("Cleaned!")


class ReusableAddressTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def serve():
    link = "http://127.0.0.1:{}/".format(conf["server_port"])
    logger.info("Serving on {}!".format(link))

    os.chdir(conf["path_to_generated_content"])

    httpd = ReusableAddressTCPServer(("", conf["server_port"]),
                                     http_server.SimpleHTTPRequestHandler)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("action")

    args = parser.parse_args()

    if args.action == "generate":
        generate()
    elif args.action == "clean":
        clean()
    elif args.action == "serve":
        serve()
    else:
        logger.error("Unknow action!")
        exit()
