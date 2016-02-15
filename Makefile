# This file has been auto-generated.
# All manual changes may be lost, see Projectfile.
#
# Date: 2016-02-15 07:33:25.578684

PYTHON ?= $(shell which python)
PYTHON_BASENAME ?= $(shell basename $(PYTHON))
PYTHON_REQUIREMENTS_FILE ?= requirements.txt
QUICK ?= 
VIRTUALENV_PATH ?= .virtualenv-$(PYTHON_BASENAME)
PIP ?= $(VIRTUALENV_PATH)/bin/pip
PYTEST_OPTIONS ?= --capture=no --cov=edgy/project --cov-report html

.PHONY: clean install lint test

# Installs the local project dependencies.
install: $(VIRTUALENV_PATH)
	if [ -z "$(QUICK)" ]; then \
	    $(PIP) install -Ue "file://`pwd`#egg=edgy.project[dev]"; \
	fi

# Setup the local virtualenv.
$(VIRTUALENV_PATH):
	virtualenv -p $(PYTHON) $(VIRTUALENV_PATH)
	$(PIP) install -U pip\>=8.0,\<9.0 wheel\>=0.24,\<1.0
	ln -fs $(VIRTUALENV_PATH)/bin/activate activate-$(PYTHON_BASENAME)

clean:
	rm -rf $(VIRTUALENV_PATH)

lint: install
	$(VIRTUALENV_PATH)/bin/pylint --py3k edgy.project -f html > pylint.html

test: install
	$(VIRTUALENV_PATH)/bin/py.test $(PYTEST_OPTIONS) tests
