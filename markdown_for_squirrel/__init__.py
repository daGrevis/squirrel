import markdown

import helpers


logger = helpers.get_logger(__name__)


def parse_content_to_markdown(context):
    if context["is_called_from_cli"]:

        arg_parser = context["arg_parser"]
        args = arg_parser.parse_args()

        if args.action == "generate":

            for page in context["pages"]:
                page["content"] = markdown.markdown(page["content"])

                logger.debug("Parsing content to Markdown for \"{}\" page..."
                            .format(page["title"]))

    return context


def inject_middlewares(middlewares):
    middlewares.add("parse_content_to_markdown", parse_content_to_markdown)

    return middlewares
