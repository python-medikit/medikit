Changelog
=========

- :release:`0.7.1 <2019-03-15>`
- :bug:`0` Remove deserialization warning (means nothing important).
- :release:`0.7.0 <2019-03-15>`
- :feature:`0` Git: now less verbose.
- :feature:`0` Kubernetes: basic helm support.
- :feature:`0` Kubernetes: patch syntax now allows to use a dotted-string to express the "patch path".
- :feature:`0` Kubernetes: supports variants to have more than one kube target.
- :feature:`0` Make: Support for "header" in makefiles, allowing to prepend arbitrary directives in generated file.
- :feature:`0` Make: Support for includes in makefiles (use `add_includes(...)`).
- :feature:`0` Make: `set_script(...)` now allows to override a predefined make target script.
- :feature:`0` Python: Support for wheelhouse (experimental, use at own risks).
- :feature:`0` Python: allows to override the setup's packages option.
- :feature:`0` Pipelines: Configuration object is now passed to pipeline for more flexibility.
- :feature:`0` Docker: DOCKER_NAME renamed to DOCKER_RUN_NAME in case of "run" task.
- :feature:`0` Uncoupling package name / version from python to use it in non-python projects.
- :feature:`0` Django: Upgraded django version.
- :feature:`0` Python: Upgraded to pip version 18.
- :feature:`0` Misc: Upgraded various python packages.
- :feature:`0` Added changelog file.
- :feature:`0` Switched internal formating to black / isort instead of yapf.
- :bug:`0` Fixed make help that would break in case of included submakefiles.
- :release:`0.6.3 <2018-05-30>`

