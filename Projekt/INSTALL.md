---
Comment: Convert with `pandoc "INSTALLATION.md" -o "INSTALLATION.pdf"`
title: INSTALLATION
author: Jonas A. Wendorf
date: \today
lang: en-US
...
# Installation for end users

Run `pip install -r requirements.txt` to install Pipenv.
Then run `pipenv install --ignore-pipfile` to install dependencies.

## Usage for end users

Run with `pipenv run python main.py`.

# Installation for developers

Run `pip install -r requirements.txt` to install Pipenv.

Then run `pipenv install --dev` to install dependencies including dependencies for development.

## Usage for developers

Run with `pipenv run python main.py`.

Use `unittests.cmd` or `unittests.sh` or `pipenv run python test.py` to run tests.

Use `checkstyle.cmd` or `checkstyle.sh` or `flake8 $FILE; pylint $FILE` to check for stylistic errors.

To regenerate documentation use `pipenv run make html`.

After you are done, use `pipenv lock` to save the changes and make sure the build stays deterministic.
