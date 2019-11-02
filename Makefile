.PHONY: bin color config install.py Makefile README.md vim zsh help
.SILENT:
.ONEFILE:

REPO="$(shell pwd)"
PACKAGE="${REPO}"/resheller
BUILD="${PACKAGE}"/build.py
PYTHON=python3

default:
	@make build
	@make clean

build:
	@"${PYTHON}" "${BUILD}"

clean:
	rm -rf build
	rm -rf dist
	find . -name "pip-wheel-metadata" -exec rm -rf {} +
	find . -name "htmlcov" -exec rm -rf {} +
	find . -name "*.spec" -exec rm -rf {} +
	find . -name ".coverage" -exec rm -rf {} +
	find . -name "*.egg-info" -exec rm -rf {} +
	find . -name "*.egg" -exec rm -rf {} +
	find . -name "*.pyc" -exec rm -rf {} +
	find . -name "*.pyo" -exec rm -rf {} +
	find . -name "*~" -exec rm -rf {} +
	find . -name "__pycache__" -exec rm -rf {} +

help:
	@echo "\033[1;33m- Usage:\033[0;0m"
	@echo "\033[0;33m- make build:\033[0;0m	Build client"
	@echo "\033[0;33m- make clean:\033[0;0m	Remove Python artifacts"
	@echo
	@echo "\033[0;33m- make help:\033[0;0m	Print this help option"
