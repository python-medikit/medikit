from __future__ import absolute_import

from .util import format_file_content


class Config(object):
    def __init__(self):
        pass


def read_configuration(dispatcher, filename, variables, features, files, setup):
    with open(filename) as f:
        code = compile(f.read(), filename, 'exec')
    ctx = {'listen': dispatcher.listen}
    exec(code, ctx)

    for k in variables.keys():
        if k in ctx:
            variables[k] = ctx[k]

    features = (features | set(ctx.pop('enable_features', ()))) - set(ctx.pop('disable_features', ()))

    for k in files.keys():
        if k in ctx:
            files[k] = format_file_content(ctx[k])

    for k in setup.keys():
        if k in ctx:
            setup[k] = ctx[k]
        if setup[k] is None:
            raise ValueError('You must provide a value for the setup entry "{}" in your Projectfile.'.format(k))

    return variables, features, files, setup
