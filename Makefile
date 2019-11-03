.SILENT:
.ONEFILE:
.PHONY: LICENSE Makefile pyproject.toml README.md requirements.txt resheller \
server.py setup.py venv

REPO="$(shell pwd)"
PACKAGE="${REPO}"/resheller
BUILD="${PACKAGE}"/build.py
CLEAN="${PACKAGE}"/clean.py
PYTHON=python3

default:
	@make build
	@make clean

build:
	@"${PYTHON}" "${BUILD}"

verbose:
	@"${PYTHON}" "${BUILD}" --verbose

install:
	@ "${PYTHON}" setup.py install
	@make default

clean:
	@"${PYTHON}" "${CLEAN}"

help:
	@echo "\033[1;33m- Usage:\033[0;0m"
	@echo "\033[0;33m- make build:\033[0;0m	Build client"
	@echo "\033[0;33m- make clean:\033[0;0m	Remove Python artifacts"
	@echo
	@echo "\033[0;33m- make help:\033[0;0m	Print this help option"
