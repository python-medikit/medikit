How to make a release?
======================

1. Pull!

.. code-block:: shell-session

   git pull

2. Update version.txt with the new version number

.. code-block:: shell-session

   VERSION_FILE=version.txt
   git fetch --tags
   git semver --next-patch > $VERSION_FILE
   git add $VERSION_FILE
   
2. (alt) Or with _version.py...

.. code-block:: shell-session

   VERSION_FILE=`python setup.py --name | sed s@\\\.@/@g`/_version.py
   git fetch --tags
   echo "__version__ = '"`git semver --next-patch`"'" > $VERSION_FILE
   git add $VERSION_FILE
   
If you have formating to do, now is the time...

.. code-block:: shell-session

   QUICK=1 make format && git add -p .

3. Run a full test, from a clean virtualenv

.. code-block:: shell

   make clean install lint test docs

4. Create the git release

.. code-block:: shell

   git commit -m "release: "`python setup.py --version`
   git tag -am `python setup.py --version` `python setup.py --version`
   git push && git push --tags

5. (open-source) Create the distribution & upload to PyPI

.. code-block:: shell

   python setup.py sdist bdist bdist_egg bdist_wheel
   twine upload dist/*-`python setup.py --version`*

5. (private) Build containers, push and patch kubernetes

.. code-block:: shell

   make release push rollout
   
