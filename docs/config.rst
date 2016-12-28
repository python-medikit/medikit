Configuration Reference
=======================

Configuration of your project goes into `Projectfile` at its root. It's a plain python file with a few locals available
to make it easy to extend the core feature of `edgy.project`.

The software will parse the file, grab the locals you defined/overrided that it cares about and then run it's
generation/update process.

Two kind of things are doable in this file:

* Define/override variables. You'll find the full reference here.
* Add event listeners to extend either core features, or feature-specific features. You'll find the reference of core
  events here, while the features event reference will be found in `features`.
