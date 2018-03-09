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






*This feature is brand new and should be used with care.*

You'll get a few make targets out of this, and a Dockerfile (or Rockerfile).

Build
-----

Building an image is as simple as running:

.. code-block:: shell-session

    $ make docker-build

This will use the root Dockerfile (or Rockerfile, see builders below) and build an image named after your package.

Push
----

You can push the built image to a docker registry, using:

.. code-block:: shell-session

    $ make docker-push

Run
---

You can run the default entrypoint / command in a new container using the built image:

.. code-block:: shell-session

    $ make docker-run

Shell
-----

You can run a bash shell in a new container using the built image:

.. code-block:: shell-session

    $ make docker-shell

Custom builder
--------------

You can change the default docker builder (a.k.a "docker build") to use rocker
(see https://github.com/grammarly/rocker).

.. code-block:: python

    docker.use_rocker_builder()

Custom image name or registry
-----------------------------

If you want to customize the image name, or the target registry (for example if you want to use Amazon Elastic 
Container Registry, Google Container Registry, Quay, or even a private registry you're crazy enough to host
yourself):

.. code-block:: python

    # only override the registry
    docker.set_remote(registry='eu.gcr.io')

    # override the registry and username, but keep the default image name
    docker.set_remote(registry='eu.gcr.io', user='sergey')

    # override the image name only
    docker.set_remote(name='acme')

    # once this is done, you must re-run the builder setup. This is a bug, tracked as #71
    docker.use_default_builder()

    # or, if you're using rocker
    docker.use_rocker_builder()

Docker Compose
--------------

The feature will also create an example docker-compose.yml file.

If you don't want this, you can:

.. code-block:: python

    docker.compose_file = None

Or if you want to override its name:

.. code-block:: python

    docker.compose_file = 'config/docker/compose.yml'

Please note that this file will only contain a structure skeleton, with no service defined. This is up to you to
fill, although we may work on this in the future as an opt-in managed file.


    


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
