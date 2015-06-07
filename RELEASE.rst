How to make a release?
======================

First, update version.txt.

.. code-block:: shell

   make lint test

Looks good?

.. code-block:: shell

   git add version.txt
   git ci -m "release: "`cat version.txt`
   git tag -am `cat version.txt` `cat version.txt`
   git push origin --tags

Now go PyPI!

.. code-block:: shell

   python setup.py sdist bdist bdist_egg bdist_wheel
   python setup.py sdist bdist bdist_egg bdist_wheel upload

