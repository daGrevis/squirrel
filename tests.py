#!/usr/bin/env python
import unittest

from squirrel import (Ware, MiddlewareDuplicationError, MiddlewareMissingError,
                      MiddlewareOrderError)


class TestWare(unittest.TestCase):

    def setUp(self):
        def fake_callable():
            pass

        self.fake_callable = fake_callable

    def test_add(self):
        middleware = Ware()
        middleware.add("a", self.fake_callable)
        with self.assertRaises(MiddlewareDuplicationError):
            middleware.add("a", self.fake_callable)

        middleware = Ware()
        with self.assertRaises(MiddlewareMissingError):
            middleware.add("b", self.fake_callable,
                           names_for_before_middlewares=["a"])

        middleware = Ware()
        with self.assertRaises(MiddlewareMissingError):
            middleware.add("a", self.fake_callable,
                           names_for_after_middlewares=["b"])

        middleware = Ware()

        middleware.add("a", self.fake_callable)
        self.assertEqual(middleware.middlewares, [("a", self.fake_callable, )])

        middleware.add("b", self.fake_callable)
        self.assertEqual(middleware.middlewares,
                         [("a", self.fake_callable, ),
                          ("b", self.fake_callable, )])

        middleware.add("c", self.fake_callable,
                       names_for_before_middlewares=["a", "b"])
        self.assertEqual(middleware.middlewares,
                         [("a", self.fake_callable, ),
                          ("b", self.fake_callable, ),
                          ("c", self.fake_callable, )])

        middleware.add("d", self.fake_callable,
                       names_for_after_middlewares=["a", "b", "c"])
        self.assertEqual(middleware.middlewares,
                         [("d", self.fake_callable, ),
                          ("a", self.fake_callable, ),
                          ("b", self.fake_callable, ),
                          ("c", self.fake_callable, )])

        with self.assertRaises(MiddlewareOrderError):
            middleware.add("e", self.fake_callable,
                           names_for_before_middlewares=["d", "a"],
                           names_for_after_middlewares=["a", "b"])

        middleware.add("e", self.fake_callable,
                       names_for_before_middlewares=["d", "a"],
                       names_for_after_middlewares=["b", "c"])
        self.assertEqual(middleware.middlewares,
                         [("d", self.fake_callable, ),
                          ("a", self.fake_callable, ),
                          ("e", self.fake_callable, ),
                          ("b", self.fake_callable, ),
                          ("c", self.fake_callable, )])

    def test_get_names_for_middlewares(self):
        middleware = Ware()

        middleware.add("a", self.fake_callable)
        self.assertEqual(middleware.get_names_for_middlewares(), ["a"])

        middleware.add("b", self.fake_callable)
        self.assertEqual(middleware.get_names_for_middlewares(), ["a", "b"])

    def test_remove(self):
        middleware = Ware()
        with self.assertRaises(MiddlewareMissingError):
            middleware.remove("a")

        middleware = Ware()

        middleware.add("a", self.fake_callable)
        middleware.remove("a")
        self.assertEqual(middleware.middlewares, [])

        middleware.add("a", self.fake_callable)
        middleware.add("b", self.fake_callable)
        middleware.remove("b")
        self.assertEqual(middleware.middlewares, [("a", self.fake_callable, )])

    def test_run(self):
        def my_callable():
            raise AssertionError()

        middleware = Ware()
        middleware.add("a", my_callable)
        with self.assertRaises(AssertionError):
            middleware.run()

        middleware = Ware()
        middleware.add("a", self.fake_callable)
        middleware.add("b", my_callable)
        with self.assertRaises(AssertionError):
            middleware.run()


if __name__ == "__main__":
    unittest.main()
