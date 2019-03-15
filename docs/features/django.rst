.. This file is auto-generated (see bin/generate_apidoc.py), do not change it manually, your changes would be overriden.

Django Feature
==============

.. automodule:: medikit.feature.django

Usage
:::::



To use the Django Feature, make sure your **Projectfile** contains the following:

.. code-block:: python

    from medikit import require
    
    django = require('django')
    
The `django` handle is a :class:`DjangoConfig` instance, and can be used to customize the feature.






This will add a few items to your Makefile, and ensure a minimalistic django project structure is available.

By default, it will use Django ~=2.0,<2.2, but you can tune that:

.. code-block:: python

    django.version = '~=2.0.3'

This feature will also add or extend a "prod" python extra, that will install gunicorn.


    





Configuration
:::::::::::::

.. autoclass:: DjangoConfig
    :members:
    :undoc-members:

Implementation
::::::::::::::

.. autoclass:: DjangoFeature
    :members:
    :undoc-members:
