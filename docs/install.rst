Quick Start
===========

Medikit is a release engineering tool provided as an eventual dependency, which means that using it won't make it
a dependency of your project. You just need to install it to update the project assets, that will be statically updated
and commited within your source control system.

Users and developpers that don't need to update the project assets wont need it, and won't even need to know it was
used. This also means that you can use it for a while, and stop using it if you think it does not suit your needs
anymore. Or you can easily add its usage to an existing project.


Installation
::::::::::::

Use the pip, luke:

.. code-block:: shell-session

    $ pip install medikit

First Steps
:::::::::::

Bootstrap a project:

.. code-block:: shell-session

    $ medikit init myproject
    $ cd myproject
    $ make install

Edit the configuration:

.. code-block:: shell-session

    $ vim Projectfile

Update a project's assets:

.. code-block:: shell-session

    $ medikit update

... or ...

.. code-block:: shell-session

    $ make update

