from whistle import Event


class MakefileEvent(Event):
    def __init__(self, package_name, makefile, config):
        self.package_name = package_name
        self.makefile = makefile
        self.config = config
        super(MakefileEvent, self).__init__()