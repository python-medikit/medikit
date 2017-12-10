Features Reference
==================

Features are the base building blocks of Medikit. In each project, you can "require" a bunch of features, it will
tell medikit what to handle.

Each feature works the same, giving you a "configuration" object when you require it. You can use this configuration
object to change the default behaviour of Medikit.

For example, to add a requirement to the python feature, write in your Projectfile:

.. code-block:: python

    from medikit import require

    python = require('python')

    python.add_requirements('requests >=2,<3')


For custom behaviors that goes further than just changing feature configurations, you can listen to a number of events
exposed by the features.

Here is an example:

.. code-block:: python

    from medikit import require, listen

    make = require('make')

    @listen(make.on_generate)
    def on_make_generate(event):
        event.makefile.add_target(
            'hello',
            'echo "Hello world"',
            phony=True
        )

.. toctree::
    :maxdepth: 1

    features/django
    features/docker
    features/git
    features/make
    features/nodejs
    features/pylint
    features/pytest
    features/python
    features/sphinx
    features/webpack
    features/yapf
