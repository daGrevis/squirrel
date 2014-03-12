import pprint


# Each middleware must accept and return `context`.
def pprint_conf(context):
    pprint.pprint(context["conf"])
    return context


# It can modify `context`.
def answer_to_life_universe_and_everything(context):
    context["conf"]["answer_to_life_universe_and_everything"] = 42
    return context


# Each plugin must have `inject_middlewares` callable that can modify
# `middlewares` using Ware API. It should must return them at the end.
def inject_middlewares(middlewares):
    # Adds middleware that updates context.
    middlewares.add("answer_to_life_universe_and_everything",
                    answer_to_life_universe_and_everything)

    # Adds middleware that pretty-prints conf w/o modifying context.
    middlewares.add("pprint_conf", pprint_conf)

    return middlewares
