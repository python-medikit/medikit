import os
from textwrap import dedent

from jinja2 import Environment, Template

from medikit.config.loader import load_feature_extensions
from medikit.settings import DEFAULT_FEATURES

env = Environment()
env.filters["underline"] = lambda s, c: s + "\n" + c * len(s)

TEMPLATE = env.from_string(
    """
.. This file is auto-generated (see bin/generate_apidoc.py), do not change it manually, your changes would be overriden.

{{ title | underline('=') }}

.. automodule:: {{ module }}

Usage
:::::

{% if is_default %}

The {{ title }} feature is required, and enabled by default.

To get a handle to the :class:`{{ config_class }}` instance, you can:

.. code-block:: python

    from medikit import require
    
    {{ name }} = require('{{ name }}')

{% else %}

To use the {{ title }}, make sure your **Projectfile** contains the following:

.. code-block:: python

    from medikit import require
    
    {{ name }} = require('{{ name }}')
    
The `{{ name }}` handle is a :class:`{{ config_class }}` instance, and can be used to customize the feature.

{% endif %}

{% if usage %}

{{ usage }}
    
{% endif %}

{% if usage_file %}

.. include:: _usage/{{ name }}.rst
    
{% endif %}


{% if has_custom_config -%}

Configuration
:::::::::::::

.. autoclass:: {{ config_class }}
    :members:
    :undoc-members:
    
{%- endif %}

Implementation
::::::::::::::

.. autoclass:: {{ feature_class }}
    :members:
    :undoc-members:

""".strip()
    + "\n\n"
)


def main():
    root_path = os.path.realpath(os.path.join(os.path.dirname(os.path.join(os.getcwd(), __file__)), ".."))
    doc_path = os.path.join(root_path, "docs")

    features = load_feature_extensions()

    for name in sorted(features):
        feature = features[name]
        module = feature.__module__
        config = feature.Config
        config_module = config.__module__
        is_default = name in DEFAULT_FEATURES

        usage = getattr(config, "__usage__", None)
        if usage:
            usage = dedent(usage.strip("\n"))

        rst = TEMPLATE.render(
            name=name,
            title=feature.__name__.replace("Feature", " Feature"),
            module=module,
            has_custom_config=(module == config_module),
            config_class=config.__name__,
            feature_class=feature.__name__,
            usage=usage,
            usage_file=os.path.exists(os.path.join(doc_path, "features/_usage", name + ".rst")),
            is_default=is_default,
        )

        with open(os.path.join(doc_path, "features", name + ".rst"), "w+") as f:
            f.write(rst)


if __name__ == "__main__":
    main()
