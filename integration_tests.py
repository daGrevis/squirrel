#!/usr/bin/env python
import unittest
import subprocess
import os
import tempfile

import splinter

import squirrel


conf = squirrel.get_conf()


class TestCommands(unittest.TestCase):
    def test_clean(self):
        try:
            os.mkdir(conf["path_to_generated_content"])
        except FileExistsError:
            pass
        tempfile.mkstemp(dir=conf["path_to_generated_content"])

        output = subprocess.check_output(["./squirrel.py", "clean"])
        self.assertIn(b"Cleaned `generated_content/`!", output)

        dir_contents = os.listdir(conf["path_to_generated_content"])
        self.assertEqual(dir_contents, [])


if __name__ == "__main__":
    unittest.main()
