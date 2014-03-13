#!/usr/bin/env python
import unittest
import subprocess
import os
import os.path as path
import shutil
import tempfile

import splinter

import squirrel


conf = squirrel.get_conf()


class TestCommands(unittest.TestCase):
    def setUp(self):
        os.mkdir(conf["path_to_articles"])
        os.mkdir(conf["path_to_generated_content"])

    def tearDown(self):
        shutil.rmtree(conf["path_to_articles"])
        shutil.rmtree(conf["path_to_generated_content"])

    def test_generate(self):
        path_to_article_dir = path.join(conf["path_to_articles"], "foobar")
        os.mkdir(path_to_article_dir)

        path_to_metadata_file = path.join(
            path_to_article_dir,
            "metadata.toml"
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
            path_to_article_dir,
            "content.txt"
        )
        with open(path_to_content_file, "w") as content_file:
            content_file.write("Hello, world!")

        output = subprocess.check_output(["./squirrel.py", "generate"])
        self.assertIn(b"Generated in `generated_content/`!", output)

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

        output = subprocess.check_output(["./squirrel.py", "clean"])
        self.assertIn(b"Cleaned `generated_content/`!", output)

        dir_contents = os.listdir(conf["path_to_generated_content"])
        self.assertEqual(dir_contents, [])



if __name__ == "__main__":
    unittest.main()
