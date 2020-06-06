# interop_clients

[![Build Status](https://travis-ci.com/ncsuarc/interop_clients.svg?branch=master)](https://travis-ci.com/ncsuarc/interop_clients)

Interoperability client for the Aerial Robotics Club at NC State.

## Development

We use [tox] as our test automation tool. If you don't already have it
installed, we strongly recommend you do because it will automatically set up
your test environment and run all of our checks. Usage is as simple as

```sh
# If you don't already have tox installed, install it
$ pip install --user tox
# Run the tests!
$ tox
```

[tox]: https://tox.readthedocs.io/en/latest/

This performs the same checks that [Travis] will run on every PR.

[Travis]: https://travis-ci.com/github/ncsuarc/interop_clients

For manual testing, we recommend [poetry] as your Python virtual environment
manager. It will automatically install all dependencies into a local venv and
should integrate with your editor nicely. We won't go over usage extensively
here, but use `poetry run` to run one-off commands in your virtualenv and
`poetry shell` to activate your virtualenv.

[poetry]: https://python-poetry.org/
