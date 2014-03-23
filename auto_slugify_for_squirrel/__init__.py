import helpers

import slugify


logger = helpers.get_logger(__name__)

args = helpers.get_args()


def auto_slugify(context):
    if args.action != "generate":
        return context

    for page in context["pages"]:
        if "slug" in page:
            continue

        page["slug"] = slugify.slugify(page["title"])

        logger.debug("Adding `{}` as slug for `{}` page..."
                     .format(page["slug"], page["title"]))

    return context


def inject_middlewares(middlewares):
    middlewares.add("auto_slugify", auto_slugify)

    return middlewares
