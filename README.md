![Squirrel](http://i.imgur.com/ibp6Bhc.jpg)

Current commands:

* `./squirrel.py generate`,

* `./squirrel.py clean`,

* `./squirrel.py serve`;

    articles
    ├── 2014
    │   └── 04
    │       └── april-fools
    │           ├── content.md
    │           └── metadata.toml
    └── hello-world
        ├── content.md
        └── metadata.toml

Location for article directories doesn't matter until they are somewhere in
`path_to_generated_content` constant defined in `conf.toml` configuration. Each
article must have `metadata.toml` file that should contain at least `title`,
`slug`, `created` and `content_path` (pointer to content file) constants.
