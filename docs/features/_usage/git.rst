Currently, **this feature is required for medikit to work**.

To disable it, use:

.. code-block:: python

    git.disable()

It will avoid creating a `.git` repository, and won't `git add` the modified files to git neither.

Even disabled, the feature will still manage the `.gitignore` file (can't harm) and the `VERSION` variable, still
based on `git describe` value. It means that you can ask medikit to not create a repo, but it should still be in a
sub-directory or a git repository somewhere.

