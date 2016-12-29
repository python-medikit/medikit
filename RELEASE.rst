How to make a release?
======================

1. Update version.txt with the new version number

.. code-block:: shell-session

   git fetch --tags
   git semver --next-patch > version.txt
   
Or with _version.py...

.. code-block:: shell-session

   echo "__version__ = '"`git semver --next-patch`"'" > `python setup.py --version`/_version.py
   

2. Run a full test, from a clean virtualenv

.. code-block:: shell

   make clean install lint test doc

3. Create the git release

.. code-block:: shell

   git add version.txt
   git commit -m "release: "`python setup.py --version`
   git tag -am `python setup.py --version` `python setup.py --version`
   git push && git push --tags

4. Create the distribution

.. code-block:: shell

   python setup.py sdist bdist bdist_egg bdist_wheel

5. Upload to PyPI

.. code-block:: shell

   twine upload dist/*-`python setup.py --version`*

