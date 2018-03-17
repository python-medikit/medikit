.. This file is auto-generated (see bin/generate_apidoc.py), do not change it manually, your changes would be overriden.

Docker Feature
==============

.. automodule:: medikit.feature.docker

Usage
:::::



To use the Docker Feature, make sure your **Projectfile** contains the following:

.. code-block:: python

    from medikit import require
    
    docker = require('docker')
    
The `docker` handle is a :class:`DockerConfig` instance, and can be used to customize the feature.







.. include:: _usage/docker.rst
    



Configuration
:::::::::::::

.. autoclass:: DockerConfig
    :members:
    :undoc-members:

Implementation
::::::::::::::

.. autoclass:: DockerFeature
    :members:
    :undoc-members:
