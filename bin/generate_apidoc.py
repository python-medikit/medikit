import os

from jinja2 import Template, Environment
from medikit.config import load_features

env = Environment()
env.filters['underline'] = lambda s, c: s + '\n' + c * len(s)

TEMPLATE = env.from_string(
    '''
.. comment:: This file is auto-generated (see bin/generate_apidoc.py), please do not change it.

{{ title | underline('=') }}

.. automodule:: {{ module }}

Usage
:::::

To use the {{ title }} feature, make sure your **Projectfile** contains:

.. code-block:: python

    from medikit import require
    
    {{ name }} = require('{{ name }}')

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

'''.strip() + '\n\n'
)


def main():
    root_path = os.path.realpath(os.path.join(os.path.dirname(os.path.join(os.getcwd(), __file__)), '..'))
    doc_path = os.path.join(root_path, 'docs')

    features = load_features()

    for name in sorted(features):
        feature = features[name]
        module = feature.__module__
        config = feature.Config
        config_module = config.__module__

        rst = TEMPLATE.render(
            name=name,
            title=feature.__name__.replace('Feature', ' Feature'),
            module=module,
            has_custom_config=(module == config_module),
            config_class=config.__name__,
            feature_class=feature.__name__,
        )

        with open(os.path.join(doc_path, 'features', name + '.rst'), 'w+') as f:
            f.write(rst)


if __name__ == '__main__':
    main()
