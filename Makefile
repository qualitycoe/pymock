# Makefile for managing a Hatch-based Python project

# Use bash so we can rely on certain bash features if needed
SHELL := /usr/bin/env bash

# Variables
DOCKER_IMAGE = pymock-test
DOCKER = docker

# Declare these as PHONY targets, so make doesn't look for real files named after these targets.
.PHONY: all install lint fmt type test test-all cov coverage docs build publish clean \
        git-status git-add git-commit git-push tag release \
        precommit-install precommit-run precommit-autoupdate

# 1) Install/Setup: ensures Hatch environment(s) exist
install:
	hatch env create
	hatch env show

# 2) Lint: checks code style & formatting (Ruff + Black)
lint:
	hatch run lint:style

# 3) Format: auto-fix style issues (Black + Ruff), then re-check
fmt:
	hatch run lint:fmt

# 4) Type: runs Mypy checks in the 'types' environment
type:
	hatch run types:check

# 5) Test: runs tests in the default environment
test:
	hatch run test

# 6) Test-All: runs tests on all Python versions defined in [tool.hatch.envs.all.matrix]
test-all:
	hatch run all:test

# 7) Cov: runs coverage-enabled tests
cov:
	hatch run test-cov

# 8) Coverage: merges parallel coverage data & prints the summary
coverage:
	hatch run cov-report

# 9) Docs: builds Sphinx documentation
docs:
	hatch run docs:build

# 10) Build: creates source & wheel distributions under 'dist/'
build:
	hatch build

# 11) Publish: publishes the built distributions to PyPI (or configured repo)
publish:
	hatch publish

# 12) Clean: remove build artifacts, coverage files, etc.
clean:
	rm -rf build dist *.egg-info .coverage .coverage.* docs/_build

# --- Git-related goals ---

# Git status: show the current repository status.
git-status:
	git status

# Git add: add all changed files to staging.
git-add:
	git add .

# Git commit: prompt for a commit message and commit changes.
git-commit:
	@read -p "Enter commit message: " msg; \
	git commit -m "$$msg"

# Git push: push committed changes to the remote repository.
git-push:
	git push

# Tag: prompt for a new tag (in calver format, e.g. YYYY.MM.DD), create it, and push to remote.
tag:
	@read -p "Enter new tag (format YYYY.MM.DD): " t; \
	git tag $$t && git push origin $$t

# Release: combine tagging, building, and publishing.
release: tag build publish

# --- Pre-commit Goals ---

# precommit-install: Install the pre-commit hooks into your repository.
precommit-install:
	pre-commit install

# precommit-run: Run all pre-commit hooks against all files.
precommit-run:
	pre-commit run --all-files

# precommit-autoupdate: Update all pre-commit hook versions to the latest.
precommit-autoupdate:
	pre-commit autoupdate

# Build Docker image
dcb:
	$(DOCKER) build -t $(DOCKER_IMAGE) .

# Run tests in Docker
dct: dcb
	$(DOCKER) run --rm $(DOCKER_IMAGE)

# Clean up Docker image (optional)
dcc:
	$(DOCKER) rmi $(DOCKER_IMAGE) || true
