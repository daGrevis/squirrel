def inject_middlewares(middlewares):
    middlewares.add("add_2", lambda x: x + 2)
    return middlewares
