.. This file is auto-generated (see bin/generate_apidoc.py), do not change it manually, your changes would be overriden.

Sphinx Feature
==============

.. automodule:: medikit.feature.sphinx

Usage
:::::



To use the Sphinx Feature, make sure your **Projectfile** contains the following:

.. code-block:: python

    from medikit import require
    
    sphinx = require('sphinx')
    
The `sphinx` handle is a :class:`SphinxConfig` instance, and can be used to customize the feature.







.. include:: _usage/sphinx.rst
    



Configuration
:::::::::::::

.. autoclass:: SphinxConfig
    :members:
    :undoc-members:

Implementation
::::::::::::::

.. autoclass:: SphinxFeature
    :members:
    :undoc-members:
