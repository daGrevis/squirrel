import markdown


def markdownify_content(context):
    for article in context["articles"]:
        article["content"] = markdown.markdown(article["content"])
    return context


def inject_middlewares(middlewares):
    middlewares.add("markdownify_content", markdownify_content)

    return middlewares
