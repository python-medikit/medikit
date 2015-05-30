class VirtualenvFeature(object):
    def __init__(self, dispatcher):
        dispatcher.add_listener('edgy.project.on_start', self.on_start, priority=-99)

    def on_start(self, event):
        pass # todo ? or makefile responsability ? or bundled in python feature ?

__feature__ = VirtualenvFeature
