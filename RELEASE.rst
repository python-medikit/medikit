How to make a release?
======================

Considering the main project repository is setup as "upstream" remote for git...

1. Pull and check dependencies are there.

.. code-block:: shell-session

   git pull upstream `git rev-parse --abbrev-ref HEAD`
   pip install -U pip wheel twine git-semver medikit

2. Update version.txt with the new version number

.. code-block:: shell-session

   VERSION_FILE=`python setup.py --name | sed s@\\\.@/@g`/_version.py
   git fetch upstream --tags
   echo "__version__ = '"`git semver --next-patch`"'" > $VERSION_FILE
   git add $VERSION_FILE

And maybe update the frozen dependencies and makefile content (medikit managed projects only)

.. code-block:: shell-session

    make update-requirements

Generate a changelog...

.. code-block:: shell-session

   git log --oneline --no-merges --pretty=format:"* %s (%an)" `git tag | tail -n 1`..
   
And paste it to project changelog, then format a bit. Everything that only concerns non-code stuff should be removed (documentation, etc.) and maybe some commits grouped so it's more readable for an human, and more logically organized than the raw git log.

.. code-block:: shell-session

   vim docs/changelog.rst

If you have formating to do, now is the time...

.. code-block:: shell-session

   QUICK=1 make format && git add -p .

3. Run a full test, from a clean virtualenv

.. code-block:: shell

   make clean install test docs

4. Create the git release

.. code-block:: shell

   git commit -m "release: "`python setup.py --version`
   git tag -am `python setup.py --version` `python setup.py --version`
   
   # Push to origin
   git push origin `git rev-parse --abbrev-ref HEAD` --tags
   
   # Push to upstream
   git push upstream `git rev-parse --abbrev-ref HEAD` --tags

5. (open-source) Create the distribution in a sandbox directory & upload to PyPI.

.. code-block:: shell

    (VERSION=`python setup.py --version`; rm -rf .release; mkdir .release; git archive `git rev-parse $VERSION` | tar xf - -C .release; cd .release/; python setup.py sdist bdist bdist_egg bdist_wheel; pip install -U twine; twine upload dist/*-`python setup.py --version`*)

Or multi version...

.. code-block:: shell

    pip install -U twine; (VERSION=`python setup.py --version`; rm -rf .release; mkdir .release; git archive `git rev-parse $VERSION` | tar xf - -C .release; cd .release/; for v in 3.5 3.6 3.7; do pip$v install -U wheel; python$v setup.py sdist bdist_egg bdist_wheel; done; twine upload dist/*-`python setup.py --version`*)

And maybe, test that the release is now installable...

.. code-block:: shell

    (name=`python setup.py --name`; for v in 3.5 3.6 3.7; do python$v -m pip install -U virtualenv; python$v -m virtualenv -p python$v .rtest$v; cd .rtest$v; bin/pip --no-cache-dir install $name; bin/python -c "import $name; print($name.__name__, $name.__version__);"; cd ..; rm -rf .rtest$v; done; )

5. (private) Build containers, push and patch kubernetes

.. code-block:: shell

   make release push rollout
   

5. (private, old gen) Deploy with capistrano

.. code-block:: shell

   cap (pre)prod deploy



*All this process is currently being migrated to "medikit pipelines" (alpha feature).*

.. code-block:: shell

   medikit pipeline release start
   
*Use at own risks*
