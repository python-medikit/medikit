How to make a release?
======================

1. Update version.txt with the new version number

.. code-block:: shell

   git semver --next-patch > version.txt

2. Run a full test, from a clean virtualenv

.. code-block:: shell

   deactivate  # be sure you're not in a virtualenv
   make clean install lint test doc

3. Create the git release

.. code-block:: shell

   git add version.txt
   git commit -m "release: "`cat version.txt`
   git tag -am `cat version.txt` `cat version.txt`
   git push origin master --tags

4. Publish to PyPI

.. code-block:: shell

   python setup.py sdist bdist bdist_egg bdist_wheel
   python setup.py sdist bdist bdist_egg bdist_wheel upload

