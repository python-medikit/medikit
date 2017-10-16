DJANGO_VERSION = 2.0.x
BASE_URL ?= https://raw.githubusercontent.com/django/django/stable/$(DJANGO_VERSION)/django/conf/project_template

.PHONY: all clean

all: urls.py.j2 wsgi.py.j2 settings.py.j2 manage.py.j2
	rm -f *.py-tpl

%.py.j2: %.py-tpl
	sed -E 's/{{[[:space:]]*project_name }}.(settings|urls|wsgi)/{{ config_package }}.\1/g' $< > $@

manage.py-tpl:
	wget $(BASE_URL)/$@ -O $@

%.py-tpl:
	wget $(BASE_URL)/project_name/$@ -O $@

clean:
	rm -f *.j2
	rm -f *.py-tpl


