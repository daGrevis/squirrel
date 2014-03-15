#!/usr/bin/env python
import unittest
import subprocess
import os
import os.path as path
import shutil
import tempfile

import squirrel


conf = squirrel.get_conf("test_conf")


class TestCommands(unittest.TestCase):
    def setUp(self):
        os.mkdir(conf["path_to_pages"])
        os.mkdir(conf["path_to_generated_content"])

    def tearDown(self):
        shutil.rmtree(conf["path_to_pages"])
        shutil.rmtree(conf["path_to_generated_content"])

    def test_generate(self):
        path_to_page_dir = path.join(conf["path_to_pages"], "foobar")
        os.mkdir(path_to_page_dir)

        path_to_metadata_file = path.join(
            path_to_page_dir,
            conf["path_to_metadata_file"]
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

        expected_output = ("Generated in `{}`!"
                           .format(conf["path_to_generated_content"])).encode()
        actual_output = subprocess.check_output(["./squirrel.py",
                                                 "generate",
                                                 "--conf-name=test_conf"])
        self.assertIn(expected_output, actual_output)

        path_to_index_file = path.join(
            conf["path_to_generated_content"],
            "foobar/index.html"
        )
        with open(path_to_index_file) as index_file:
            content_of_index_file = index_file.read()

        self.assertIn("Foobar", content_of_index_file)
        self.assertIn("Hello, world!", content_of_index_file)

    def test_clean(self):
        tempfile.mkstemp(dir=conf["path_to_generated_content"])

        expected_output = ("Cleaned `{}`!"
                           .format(conf["path_to_generated_content"])).encode()
        actual_output = subprocess.check_output(["./squirrel.py",
                                                 "clean",
                                                 "--conf-name=test_conf"])
        self.assertIn(expected_output, actual_output)

        dir_contents = os.listdir(conf["path_to_generated_content"])
        self.assertEqual(dir_contents, [])


if __name__ == "__main__":
    unittest.main()
