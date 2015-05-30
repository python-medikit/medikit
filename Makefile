PYTHON ?= $(VIRTUALENV_PATH)/bin/python
VIRTUALENV_PATH ?= .python-virtualenv
WHEELHOUSE_PATH ?= .python-wheelhouse
PYTHON_PIP ?= $(VIRTUALENV_PATH)/bin/pip --cache-dir=$(PIPCACHE_PATH)
PIPCACHE_PATH ?= .python-pipcache

.PHONY: test install

install: $(VIRTUALENV_PATH)
	$(PYTHON_PIP) wheel -w $(WHEELHOUSE_PATH) -f $(WHEELHOUSE_PATH) -r requirements.txt
	$(PYTHON_PIP) install -f $(WHEELHOUSE_PATH) -U -r requirements.txt

$(VIRTUALENV_PATH):
	virtualenv $(VIRTUALENV_PATH)
	$(PYTHON_PIP) install -U pip\>=7.0,\<8.0 wheel\>=0.24,\<1.0
	ln -fs $(VIRTUALENV_PATH)/bin/activate

test: install
	nosetests -q --with-doctest --with-coverage --cover-package=edgy.project
