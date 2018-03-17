.. This file is auto-generated (see bin/generate_apidoc.py), do not change it manually, your changes would be overriden.

Kube Feature
============

.. automodule:: medikit.feature.kube

Usage
:::::



To use the Kube Feature, make sure your **Projectfile** contains the following:

.. code-block:: python

    from medikit import require
    
    kube = require('kube')
    
The `kube` handle is a :class:`KubeConfig` instance, and can be used to customize the feature.







.. include:: _usage/kube.rst
    



Configuration
:::::::::::::

.. autoclass:: KubeConfig
    :members:
    :undoc-members:

Implementation
::::::::::::::

.. autoclass:: KubeFeature
    :members:
    :undoc-members:
