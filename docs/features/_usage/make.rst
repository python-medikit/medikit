Currently, **this feature is required for medikit to work**.

Makefile generation and management is quite central to medikit, and it's one of the strongest opinionated choices
made by the tool.

.. note:: `Makefile` will be overriden on each `medikit update` run! See below how to customize it.

Everything out of the project's world is managed by a single, central Makefile, that contains all the external
entrypoints to your package.

By default, it only contains the following targets (a.k.a "tasks"):

* install
* install-dev
* update
* update-requirements

This is highly extendable, and about all other features will add their own targets using listeners to the
:obj:`MakeConfig.on_generate` event.

Default targets
---------------

Install
.......

The `make install` command will try its best to install your package in your current system environment. For python
projects, it work with the system python, but you're highly encouraged to use a virtual environment (using
:mod:`virtualenv` or :mod:`venv` module).

.. code-block:: shell-session

    $ make install

Install Dev
...........

The `make install-dev` command works like `make install`, but adds the `dev` extra.

The `dev` extra is a convention medikit takes to group all dependencies that are only required to actual hack on
your project, and that won't be necessary in production / runtime environments.

For python projects, it maps to an "extra", as defined by setuptools. For Node.js projects, it will use the
"devDependencies".

.. code-block:: shell-session

    $ make install-dev

Update
......

This is a shortcut to `medikit update`, with a preliminary dependency check on `medikit`.

As you may have noticed, `medikit` is never added as a dependency to your project, so this task will ensure it's
installed before running.

.. code-block:: shell-session

    $ make update

Update Requirements
...................

The `make update-requirements` command works like `make update`, but forces the regeneration of `requirements*.txt`
files.

For security reasons, `medikit` never updates your requirements if they are already frozen in requirements files
(you would not want a requirement to increment version without notice).

This task is here so you can explicitely update your requirements frozen versions, according to the constraints
you defined in the `Projectfile`.

.. code-block:: shell-session

    $ make update-requirements

Customize your Makefile
-----------------------

To customize the generated `Makefile`, you can use the same event mechanism that is used by `medikit` features,
directly from within your `Projectfile`.

Add a target
............

.. code-block:: python

    from medikit import listen

    @listen(make.on_generate)
    def on_make_generate(event):
        event.makefile.add_target('foo', '''
                echo "Foo!"
            ''', deps=('install', ), phony=True, doc='So foo...'
        )

    This is pretty self-explanatory, but let's detail:

    * "foo" is the target name (you'll be able to run `make foo`)
    * This target will run `echo "Foo!"`
    * It depends on the `install` target, that needs to be satisfied (install being "phony", it will be run
      every time).
    * This task is "phony", meaning that there will be no `foo` file or directory generated as the output, and thus
      that `make` should consider it's never outdated.
    * If you create non phony targets, they must result in a matching file or directory created.
    * Read more about GNU Make: https://www.gnu.org/software/make/

Change the dependencies of an existing target
.............................................

.. code-block:: python

    from medikit import listen

    @listen(make.on_generate)
    def on_make_generate(event):
        event.makefile.set_seps('foo', ('install-dev', ))

Add (or override) a variable
............................

.. code-block:: python

    from medikit import listen

    @listen(make.on_generate)
    def on_make_generate(event):
        event.makefile['FOO'] = 'Bar'

The user can override `Makefile` variables using your system environment:

.. code-block:: shell-session

    $ FOO=loremipsum make foo

To avoid this default behaviour (which is more than ok most of the time), you can change the assignment operator
used in the makefile.

.. code-block:: python

    from medikit import listen

    @listen(make.on_generate)
    def on_make_generate(event):
        event.makefile.set_assignment_operator('FOO', ':=')

This is an advanced feature you'll probably never need. You can `read the make variables reference
<https://www.gnu.org/software/make/manual/html_node/Using-Variables.html#Using-Variables>`_.
