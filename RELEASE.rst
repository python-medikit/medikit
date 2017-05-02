How to make a release?
======================

Considering the main project repository is setup as "upstream" remote for git...

1. Pull and check dependencies are there.

.. code-block:: shell-session

   git pull upstream
   pip install -U pip wheel twine git-semver 

2. Update version.txt with the new version number

.. code-block:: shell-session

   VERSION_FILE=version.txt
   git fetch upstream --tags
   git semver --next-patch > $VERSION_FILE
   git add $VERSION_FILE
   
2. (alt) Or with _version.py...

.. code-block:: shell-session

   VERSION_FILE=`python setup.py --name | sed s@\\\.@/@g`/_version.py
   git fetch upstream --tags
   echo "__version__ = '"`git semver --next-patch`"'" > $VERSION_FILE
   git add $VERSION_FILE
   
If you have formating to do, now is the time...

.. code-block:: shell-session

   QUICK=1 make format && git add -p .

You can also edit the changelog ...

.. code-block:: shell-session

   vim docs/changelog.rst  

3. Run a full test, from a clean virtualenv

.. code-block:: shell

   make clean install lint test docs

4. Create the git release

.. code-block:: shell

   git commit -m "release: "`python setup.py --version`
   git tag -am `python setup.py --version` `python setup.py --version`
   git push upstream && git push upstream --tags

5. (open-source) Create the distribution & upload to PyPI

.. code-block:: shell

   python setup.py sdist bdist bdist_egg bdist_wheel
   twine upload dist/*-`python setup.py --version`*

5. (open-source, paranoid) Create the distribution & upload to PyPI in a brand new clone.

.. code-block:: shell

   (VERSION=`python setup.py --version`; rm -rf .release; mkdir .release; git archive `git rev-parse $VERSION` | tar xf - -C .release; cd .release/; python setup.py sdist bdist bdist_egg bdist_wheel; twine upload dist/*-`python setup.py --version`*)

5. (private) Build containers, push and patch kubernetes

.. code-block:: shell

   make release push rollout
   

5. (private, old gen) Deploy with capistrano

.. code-block:: shell

   cap (pre)prod deploy
