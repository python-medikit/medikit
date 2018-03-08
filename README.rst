✚ medikit ✚
===========

Strongly opinionated python 3.5+ project management.

.. image:: https://travis-ci.org/python-medikit/medikit.svg?branch=master
    :target: https://travis-ci.org/python-medikit/medikit
    :alt: Continuous Integration Status

.. image:: https://coveralls.io/repos/github/python-medikit/medikit/badge.svg?branch=master
    :target: https://coveralls.io/github/python-medikit/medikit?branch=master
    :alt: Coverage Status

.. image:: https://readthedocs.org/projects/medikit/badge/?version=latest
    :target: http://edgyproject.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Fpython-medikit%2Fmedikit.svg?type=shield
    :target: https://app.fossa.io/projects/git%2Bgithub.com%2Fpython-medikit%2Fmedikit?ref=badge_shield
    :alt: License Status

Medikit is the first-aid toolkit to manage your project's boilerplate, like
package files, versions, config, test suite, runners, ...

This package helps you create python (or not) source trees using best practices
(or at least the practices we consider as best for us) in a breeze.

Don't worry about setting up git, a makefile, usual project targets, unit tests
framework, pip, wheels, virtualenv, code coverage, namespace packages, setup.py
files ...

Medikit's got you covered on all this, using one simple and fast command.


Install
=======

Before installing the package, you must make sure that `pip` and `virtualenv`
are installed and available to be used in your current environment.

.. code-block:: shell

    pip install medikit

Now, you may want to bootstrap a python package source tree.

.. code-block:: shell

    mkdir my.awesome.pkg
    cd my.awesome.pkg
    medikit init

You're done with the bootstrap. You can now run:

.. code-block:: shell

    make install
    make test
    git commit -m 'Damn that was fast ...'

Happy?


Update
======

If you change the `Projectfile` content, or update the library, you will need to run
the generator again.

.. code-block:: shell

    medikit update

To better control what changes are made, I suggest that you run it on a clean git
repository, then look at the dofferences using:

.. code-block:: shell

    git diff --cached

You can then commit the generated changes.


Gotchas
=======

As the headline says, we have made strong opinionated choices about how a project
tree should be organized.

For example, we choose to use make to provide the main project entrypoints
(install, test). We also choose to use git. And pytest. And to put root package
in the project root (as opposed to a src dir or something like this). Etc.

For beginners, that's a good thing, because they won't have to ask themselves
questions like "What should I put in setup.py ?" or "Should I create a «src»
dir or not ?". For more advanced users, it can be either a good thing if you
agree with our choices, or a bad one ...


Architecture
============

Medikit uses a single configuration file in your project, called Projectfile.

This file contains all the specific of your project:

* What features you wanna use.
* The customizations of those features
* The additional event listeners (more on this later) you need.
* The eventual pipelines that you need.

At its heart, medikit uses an "event dispatcher" model.

An update will dispatch a "medikit.on_start" event, and features that you required
can listen (react) to this event by adding jobs to run in response. They also can
dispatch their own events.

As a result, you'll get your projects files updated, that will be a combination of
all the events listeners executed.

It means two things:

* Unlike usual project templates and generators, it can both bootstrap and update
  your project, as best practice evolves.
* It's not a dependency of your project. Once it has run, you can forget it. Either
  you choose to maintain your project assets with it and you'll need it installed
  while updating, or you can remove it and just keep the generated files.


F.A.Q
=====

* I'm using PasteScript, isn't that enough?

  * PasteScript with the basic_package template will only generate a very
    minimalistic tree, while we install a few tools and generate more boilerplate
    than it does. The fact is, we were using it before but still had a lot of
    repeated actions to do then, and the exact aim of this project is to automate
    the whole. Also, PasteScript cannot update a project once generated, while we
    do.

* Should I use it?

  * You're a grown man, right?

* Is it stable / production ready?

  * Not really relevant to this project, as it's more a development tool than
    something you'll use in operations. However, please note that on some points
    and until version 1.0, we will tune things and change the way it works to find
    the most flexible way to operate. Thus, if you relly on a specific
    implementation, updates may break things. The good news is that you'll be able
    to review changes using `git diff --cached`, and either rollback or report
    issues saying how much you're disappointed (and why, don't forget the why,
    please).

* Can I contribute?

  * Yes, but the right vs wrong choices decision is up to us. Probably a good
    idea to discuss about it (in an issue for example) first.

* Can you include feature «foo»?

  * Probably, or maybe not. Come on github issues to discuss it, if we agree on
    the fact this feature is good for a lot of usages, your patch will be
    welcome. Also, we're working on a simple way to write "feature plugins", so
    even if we don't agree on something, you'll be able to code and even distribute
    addons that make things work the way you like.

* Do you support python 3?

  * Of course, and for quite some times we decided to only support python 3, as we
    think the "10 years incubation period" we just had is a sufficient maturation
    period to just forget about python 2.


License
=======

.. image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Fpython-medikit%2Fmedikit.svg?type=large
    :target: https://app.fossa.io/projects/git%2Bgithub.com%2Fpython-medikit%2Fmedikit?ref=badge_large
    :alt: License Status

