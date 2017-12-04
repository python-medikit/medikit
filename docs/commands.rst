Commands Reference
==================


Init
::::

Creates a project (bootstraps the Projectfile, then run an update).

.. code-block:: shell-session

    $ medikit init <projectname>


Update
::::::

Updates a project, according to Projectfile.

.. code-block:: shell-session

    $ medikit update


Pipeline (alpha)
::::::::::::::::

Starts, or continue, a project management pipeline.

.. code-block:: shell-session

    $ medikit pipeline release start

If the pipeline already started, you can resume it:

.. code-block:: shell-session

    $ medikit pipeline release continue



