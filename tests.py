#!/usr/bin/env python
import unittest

from ware import (Ware, MiddlewareDuplicationError, MiddlewareMissingError,
                  MiddlewareOrderError, MiddlewareArgumentsError)


class TestWare(unittest.TestCase):

    def setUp(self):
        def dummy_callable(data):
            return data

        self.dummy_callable = dummy_callable

    def test_add(self):
        def my_callable():
            pass

        middlewares = Ware()
        with self.assertRaises(MiddlewareArgumentsError):
            middlewares.add("a", my_callable)

        middlewares = Ware()
        middlewares.add("a", self.dummy_callable)
        with self.assertRaises(MiddlewareDuplicationError):
            middlewares.add("a", self.dummy_callable)

        middlewares = Ware()
        with self.assertRaises(MiddlewareMissingError):
            middlewares.add("b", self.dummy_callable,
                            names_for_before_middlewares=["a"])

        middlewares = Ware()
        with self.assertRaises(MiddlewareMissingError):
             middlewares.add("a", self.dummy_callable,
                           names_for_after_middlewares=["b"])

        middlewares = Ware()

        middlewares.add("a", self.dummy_callable)
        self.assertEqual(middlewares.middlewares,
                         [("a", self.dummy_callable, )])

        middlewares.add("b", self.dummy_callable)
        self.assertEqual(middlewares.middlewares,
                         [("a", self.dummy_callable, ),
                          ("b", self.dummy_callable, )])

        middlewares.add("c", self.dummy_callable,
                       names_for_before_middlewares=["a", "b"])
        self.assertEqual(middlewares.middlewares,
                         [("a", self.dummy_callable, ),
                          ("b", self.dummy_callable, ),
                          ("c", self.dummy_callable, )])

        middlewares.add("d", self.dummy_callable,
                       names_for_after_middlewares=["a", "b", "c"])
        self.assertEqual(middlewares.middlewares,
                         [("d", self.dummy_callable, ),
                          ("a", self.dummy_callable, ),
                          ("b", self.dummy_callable, ),
                          ("c", self.dummy_callable, )])

        with self.assertRaises(MiddlewareOrderError):
            middlewares.add("e", self.dummy_callable,
                           names_for_before_middlewares=["d", "a"],
                           names_for_after_middlewares=["a", "b"])

        middlewares.add("e", self.dummy_callable,
                       names_for_before_middlewares=["d", "a"],
                       names_for_after_middlewares=["b", "c"])
        self.assertEqual(middlewares.middlewares,
                         [("d", self.dummy_callable, ),
                          ("a", self.dummy_callable, ),
                          ("e", self.dummy_callable, ),
                          ("b", self.dummy_callable, ),
                          ("c", self.dummy_callable, )])

    def test_get_names_for_middlewares(self):
        middlewares = Ware()

        middlewares.add("a", self.dummy_callable)
        self.assertEqual(middlewares.get_names_for_middlewares(), ["a"])

        middlewares.add("b", self.dummy_callable)
        self.assertEqual(middlewares.get_names_for_middlewares(), ["a", "b"])

    def test_remove(self):
        middlewares = Ware()
        with self.assertRaises(MiddlewareMissingError):
            middlewares.remove("a")

        middlewares = Ware()

        middlewares.add("a", self.dummy_callable)
        middlewares.remove("a")
        self.assertEqual(middlewares.middlewares, [])

        middlewares.add("a", self.dummy_callable)
        middlewares.add("b", self.dummy_callable)
        middlewares.remove("b")
        self.assertEqual(middlewares.middlewares,
                         [("a", self.dummy_callable, )])

    def test_run(self):
        def my_callable(data):
            raise AssertionError()

        middlewares = Ware()
        middlewares.add("a", my_callable)
        with self.assertRaises(AssertionError):
            middlewares.run()

        middlewares = Ware()
        middlewares.add("a", self.dummy_callable)
        middlewares.add("b", my_callable)
        with self.assertRaises(AssertionError):
            middlewares.run()

        def add_2(data):
            data["x"] += 2
            return data

        def square(data):
            data["x"] = data["x"] * data["x"]
            return data

        middlewares = Ware()
        middlewares.add("add_2", add_2)
        middlewares.add("square", square)
        context = middlewares.run({"x": 1})
        self.assertEqual(context["x"], 9)


if __name__ == "__main__":
    unittest.main()
