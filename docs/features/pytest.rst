.. This file is auto-generated (see bin/generate_apidoc.py), do not change it manually, your changes would be overriden.

Pytest Feature
==============

.. automodule:: medikit.feature.pytest

Usage
:::::



To use the Pytest Feature, make sure your **Projectfile** contains the following:

.. code-block:: python

    from medikit import require
    
    pytest = require('pytest')
    
The `pytest` handle is a :class:`PytestConfig` instance, and can be used to customize the feature.








Configuration
:::::::::::::

.. autoclass:: PytestConfig
    :members:
    :undoc-members:

Implementation
::::::::::::::

.. autoclass:: PytestFeature
    :members:
    :undoc-members:
