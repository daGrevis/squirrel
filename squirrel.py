#!/usr/bin/env python
import os
import os.path as path
import logging
import argparse
import shutil
import http.server as http_server
import socketserver
import importlib

import toml
import jinja2


from ware import Ware


REQUIRED_KEYS_IN_CONF = (
    "blog_title",
    "blog_description",
    "blog_theme",
    "plugins",
    "metadata_file",
    "index_file",
    "path_to_generated_content",
    "path_to_articles",
    "path_to_themes",
    "path_to_theme_static",
    "path_to_generated_static",
    "required_keys_in_article",
    "forbidden_keys_in_article",
    "server_port",
    "name_for_injection_callable",
)


# Inits logging.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


# Loads conf from conf.toml.
with open("conf.toml") as conf_file:
    conf = toml.loads(conf_file.read())

for key in REQUIRED_KEYS_IN_CONF:
    if key not in conf:
        logger.error("Conf is missing key `{}`!".format(key))
        exit()


# Inits templating.
path_to_theme = path.join(conf["path_to_themes"], conf["blog_theme"])
jinja2_loader = jinja2.FileSystemLoader(path_to_theme)
jinja2_env = jinja2.Environment(loader=jinja2_loader)


# Inits plugins.
middlewares = Ware()
for plugin_name in conf["plugins"]:
    try:
        plugin = importlib.import_module(plugin_name)
    except ImportError:
        logger.error("Can't load plugin `{}`!".format(plugin_name))
        exit()

    if not hasattr(plugin, conf["name_for_injection_callable"]):
        message = ("Plugin `{}` doesn't have `{}` callable!"
                   .format(plugin_name, conf["name_for_injection_callable"]))
        logger.error(message)
        exit()

    middlewares = plugin.inject_middlewares(middlewares)


context = {
    "conf": conf,
    "jinja2_env": jinja2_env,
}
middlewares.run(context)


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
        # generate()
        pass
    elif args.action == "clean":
        clean()
    elif args.action == "serve":
        serve()
    else:
        logger.error("Unknow action!")
        exit()
