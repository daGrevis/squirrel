import markdown

import helpers


logger = helpers.get_logger(__name__)


def parse_content_to_markdown(context):
    args = helpers.get_args()

    if args.action != "generate":
        return context

    for page in context["pages"]:
        page["content"] = markdown.markdown(page["content"])

        logger.debug("Parsing content to Markdown for \"{}\" page..."
                     .format(page["title"]))

    return context


def inject_middlewares(middlewares):
    middlewares.add("parse_content_to_markdown", parse_content_to_markdown)

    return middlewares
