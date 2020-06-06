# interop_clients

[![Build Status](https://travis-ci.com/ncsuarc/interop_clients.svg?branch=master)](https://travis-ci.com/ncsuarc/interop_clients)

Interoperability client for the Aerial Robotics Club at NC State.

## Development

Since we do not yet have a CI pipeline for this project, run the following
commands before merging any pull request. If you used [poetry] to set up your
virtualenv, you should already have all dependencies for the following
commands!

```sh
poetry run mypy .
poetry run flake8
poetry run pytest
poetry run black --check .
poetry run isort --check-only
```

[poetry]: https://python-poetry.org/
