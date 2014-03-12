import inspect


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


class MiddlewareArgumentsError(Exception):

    def __init__(self, middleware_name):
        message = ("Middleware `{}` has wrong count of arguments!"
                   .format(middleware_name))
        super().__init__(message)


class Ware(object):

    def __init__(self, middlewares=[]):
        self.middlewares = []

    def get_names_for_middlewares(self):
        return [name for name, _ in self.middlewares]

    def add(self, middleware_name, middleware_callable,
            names_for_before_middlewares=[], names_for_after_middlewares=[]):

        if len((inspect.getfullargspec(middleware_callable)).args) != 1:
            raise MiddlewareArgumentsError(middleware_name)

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

    def run(self, initial_context={}):
        context = initial_context
        for _, middleware_callable in self.middlewares:
            context = middleware_callable(context)
        return context
