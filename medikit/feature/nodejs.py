from medikit.events import subscribe

from . import Feature


class NodeJSFeature(Feature):
    requires = {'make'}

    @subscribe('medikit.feature.make.on_generate')
    def on_make_generate(self, event):
        event.makefile['YARN'] = '$(shell which yarn)'
        event.makefile['NODE'] = '$(shell which node)'

        event.makefile.get_target('install').install += [
            '$(YARN) install --production',
        ]

        event.makefile.get_target('install-dev').install += [
            '$(YARN) install',
        ]


__feature__ = NodeJSFeature
