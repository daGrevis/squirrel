import markdown

import helpers


logger = helpers.get_logger(__name__)


def markdownify_content(context):
    if context["is_called_from_cli"]:

        arg_parser = context["arg_parser"]
        args = arg_parser.parse_args()

        if args.action == "generate":

            for article in context["articles"]:
                article["content"] = markdown.markdown(article["content"])

                logger.debug("Parsing content to Markdown for `{}` article..."
                            .format(article["title"]))

    return context


def inject_middlewares(middlewares):
    middlewares.add("markdownify_content", markdownify_content)

    return middlewares
