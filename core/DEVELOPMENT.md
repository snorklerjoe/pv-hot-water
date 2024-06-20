# Development

All paths are relative to the root of the repository.

This document only discusses development of the Python-based code in `/core`.

## Setup

*Note: This project uses Python 3.12. If you do not have Python 3.12 installed, please do that before proceeding or otherwise create the venv with Python 3.12.*

To get started, clone the repo, and from the root of the repo, run:

``` bash
python3.12 -m venv .venv  # Create a new virtual environment

# Activate the environment (VSCode and other editors or IDEs will recognize it and may do this automatically):
source .venv/bin/activate

pip install poetry  # We use poetry to help with dependencies, building, tools, etc. Read about it.

cd core  # All of the Python code is in `core/`

poetry install
```

With that, the dependencies should be installed and everything is ready to go.

## Maintainability and Testing

As a security, reliability, safety, and maintainability measure, **do not deploy code that does not pass all checks.**  
There is a reason for each check and unit test and they should not be disabled or modified without thinking carefully.

Commits should **generally** not be pushed to the main branch unless all checks pass.

Release tags should **always** have all checks passing.

### Linting / Code Format

This project uses [flake8](https://github.com/PyCQA/flake8) as a [linter](https://en.wikipedia.org/wiki/Lint_(software)).  
The configuration for flake8 is in `/.flake8`

Run the linter as follows (from `/core`):

``` bash
poetry run flake8
```

### Type-Checking

This project uses [MyPy](https://github.com/python/mypy/) for type-checking.  

Run it like this (from `/core`):

``` bash
poetry run mypy .
```

### Unit Testing

Unit tests are important.

This project uses PyTest for unit tests and Coverage to give test coverage reports. 100% test coverage is not required (understandably, as some hardware tests are difficult to make work in a dev environment), but test coverage should be maximized.

Stuff you can do (from `/core`):

``` bash
# To run the unit tests without collecting coverage information:
poetry run pytest

# To run the unit tests and collect coverage information:
poetry run coverage run -m pytest

# To see the coverage report:
poetry run coverage report

# To see the coverage report with line numbers of places missing coverage:
poetry run coverage report -m
```

### Flask Debug Server

To test the webapp (this also applies for the api), the Flask development server may be used.  
To run the web app with development server locally on your computer, use the following (from the `/core` directory):

``` bash
FLASK_DEBUG=1 flask --app pvhotwatercore.webapp.app run
```

**TODO: add a poetry script or something based on the toml config files to facilitate this.**

A test page should exist at `/test-page/` from the root of the webserver (such as `http://localhost:5000/test-page/`).
