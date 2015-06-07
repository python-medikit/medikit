PYTHON ?= $(shell which python)
PYTHON_BASENAME ?= $(shell basename $(PYTHON))
VIRTUALENV_PATH ?= .$(PYTHON_BASENAME)-virtualenv
WHEELHOUSE_PATH ?= .$(PYTHON_BASENAME)-wheelhouse
PIPCACHE_PATH ?= .$(PYTHON_BASENAME)-pipcache
PIP ?= $(VIRTUALENV_PATH)/bin/pip --cache-dir=$(PIPCACHE_PATH)

.PHONY: test lint clean install

install: $(VIRTUALENV_PATH)
	$(PIP) wheel -w $(WHEELHOUSE_PATH) -f $(WHEELHOUSE_PATH) -r requirements.txt
	$(PIP) install -Ue .
	$(PIP) install -f $(WHEELHOUSE_PATH) -Ur requirements.txt

$(VIRTUALENV_PATH):
	virtualenv -p $(PYTHON) $(VIRTUALENV_PATH)
	$(VIRTUALENV_PATH)/bin/pip install -U pip\>=7.0,\<8.0 wheel\>=0.24,\<1.0
	ln -fs $(VIRTUALENV_PATH)/bin/activate $(PYTHON_BASENAME)-activate

clean:
	rm -rf $(VIRTUALENV_PATH) $(WHEELHOUSE_PATH) $(PIPCACHE_PATH)

lint: install
	$(VIRTUALENV_PATH)/bin/pylint --py3k edgy.project -f html > pylint.html

test: install
	$(VIRTUALENV_PATH)/bin/nosetests -q --with-doctest --with-coverage --cover-package=edgy.project
