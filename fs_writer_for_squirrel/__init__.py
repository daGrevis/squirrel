import os
import os.path as path
import shutil

import helpers


logger = helpers.get_logger(__name__)

conf = helpers.get_conf()
args = helpers.get_args()


def prepare_dir_for_build(context):
    clean_command = context["clean_command"]

    clean_command()

    try:
        os.mkdir(conf["build_dir"])
    except FileExistsError:
        pass

    logger.debug("Creating `{}`..." .format(conf["build_dir"]))


def write_to_virtual_fs(virtual_fs):
    def walk_recursively(dir, dir_path):
        for name, dir_or_file_content in dir.items():
            if isinstance(dir_or_file_content, dict):
                path_to_current_dir = path.join(dir_path, name)
                os.mkdir(path_to_current_dir)

                logger.debug("Creating `{}`...".format(path_to_current_dir))

                walk_recursively(dir_or_file_content, path_to_current_dir)
            else:
                path_to_current_file = path.join(dir_path, name)
                with open(path_to_current_file, "w") as current_file:
                    current_file.write(dir_or_file_content)

                logger.debug("Creating `{}`...".format(path_to_current_file))

    walk_recursively(virtual_fs, conf["build_dir"])


def generate_static_for_theme(context):
    path_to_theme_static = path.join(conf["theme_dir"],
                                     conf["dir_for_build_static"])
    path_to_generated_static = path.join(
        conf["build_dir"],
        conf["dir_for_build_static"]
    )

    shutil.copytree(path_to_theme_static, path_to_generated_static)

    logger.debug("Copying static from `{}` to `{}`...".
                 format(path_to_theme_static, path_to_generated_static))


def fs_writer(context):
    if args.action != "generate":
        return context

    prepare_dir_for_build(context)
    write_to_virtual_fs(context["virtual_fs"])

    generate_static_for_theme(context)  # TODO: Hello! Where do I belong?

    logger.info("Generated `{}`!" .format(conf["build_dir"]))

    return context


def inject_middlewares(middlewares):
    middlewares.add("fs_writer", fs_writer)

    return middlewares
