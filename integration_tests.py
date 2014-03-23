#!/usr/bin/env python
import unittest
import subprocess
import os
import os.path as path
import shutil
import tempfile

import helpers


conf = helpers.get_conf("test_conf")


class TestCommands(unittest.TestCase):
    def setUp(self):
        os.mkdir(conf["source_dir"])
        os.mkdir(conf["build_dir"])

    def tearDown(self):
        shutil.rmtree(conf["source_dir"])
        shutil.rmtree(conf["build_dir"])

    def test_generate(self):
        path_to_page_dir = path.join(conf["source_dir"], "foobar")
        os.mkdir(path_to_page_dir)

        path_to_metadata_file = path.join(
            path_to_page_dir,
            conf["metadata_file"]
        )
        metadata_content = (
            'title = "Foobar"\n'
            'slug = "foobar"\n'
            'author = "daGrevis"\n'
            'created = 2014-01-01T00:00:00Z\n'
            'content_path = "content.txt"'
        )
        with open(path_to_metadata_file, "w") as metadata_file:
            metadata_file.write(metadata_content)

        path_to_content_file = path.join(
            path_to_page_dir,
            "content.txt"
        )
        with open(path_to_content_file, "w") as content_file:
            content_file.write("Hello, world!")

        expected_output = ("Generated `{}`!"
                           .format(conf["build_dir"])).encode()
        actual_output = subprocess.check_output(["./squirrel.py",
                                                 "generate",
                                                 "--conf-name=test_conf"])
        self.assertIn(expected_output, actual_output)

        path_to_index_file = path.join(
            conf["build_dir"],
            "pages/foobar/index.html"
        )
        with open(path_to_index_file) as index_file:
            content_of_index_file = index_file.read()

        self.assertIn("Foobar", content_of_index_file)
        self.assertIn("Hello, world!", content_of_index_file)

    def test_clean(self):
        tempfile.mkstemp(dir=conf["build_dir"])

        expected_output = ("Cleaned `{}`!"
                           .format(conf["build_dir"])).encode()
        actual_output = subprocess.check_output(["./squirrel.py",
                                                 "clean",
                                                 "--conf-name=test_conf"])
        self.assertIn(expected_output, actual_output)

        dir_contents = os.listdir(conf["build_dir"])
        self.assertEqual(dir_contents, [])


if __name__ == "__main__":
    unittest.main()
