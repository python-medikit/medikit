You can customize the theme:

.. code-block:: python

    sphinx.theme = 'sphinx_rtd_theme'

Note that this should be a parsable requirement, and it won't be added to your docs/conf.py automatically.

This feature will add the necessary requirements to the python feature (sphinx mostly, and eventually your theme requirement) and setup the correct makefile task to build the html docs. Note that it won't bootstrap your sphinx config file, and you still need to run the following if your documentation does not exist yet:

.. code-block:: shell-session

    $ make update-requirements
    $ make install-dev
    $ mkdir docs
    $ cd docs
    $ sphinx-quickstart .

Then, eventually tune the configuration.

.. note::

    In the future, we may consider generating it for you if it does not exist, but it's not a priority.

