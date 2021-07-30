# Self-Documented Makefile see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html

.DEFAULT_GOAL := help
PART 	:= minor

# Put it first so that "make" without argument is like "make help".
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-32s-\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

guard-%: ## Checks that env var is set else exits with non 0 mainly used in CI;
	@if [ -z '${${*}}' ]; then echo 'Environment variable $* not set' && exit 1; fi

# --------------------------------------------------------
# ------- Python package (pip) management commands -------
# --------------------------------------------------------

clean: clean-build clean-pyc  ## remove all build and Python artifacts

clean-build:  ## remove build artifacts
	@rm -fr build/
	@rm -fr dist/
	@rm -fr .eggs/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +

clean-pyc:  ## remove Python file artifacts
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} + || true

lint:  ## check style with flake8
	@flake8 github_deploy

release: dist  ## package and upload a release
	@twine upload dist/*

dist: clean install-deploy  ## builds source and wheel package
	@pip install twine==3.4.1
	@python setup.py sdist bdist_wheel

increase-version: guard-PART  ## Increase project version
	@bump2version $(PART)
	@git switch -c main

install-wheel: clean  ## Install wheel
	@echo "Installing wheel..."
	@pip install wheel

install: install-wheel  ## install the package to the active Python's site-packages
	@pip install .

install-deploy: install-wheel
	@pip install -e .'[deploy]'

migrations:
	@python manage.py makemigrations

.PHONY: clean clean-build clean-pyc dist increase-version install-wheel install install-deploy increase-version lint release migrations
