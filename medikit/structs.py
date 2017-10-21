import textwrap


class Script(object):
    def __init__(self, script=None):
        self.script = self.parse_script(script)

    def parse_script(self, script):
        if not script:
            return []
        script = textwrap.dedent(str(script)).strip()
        return script.split('\n')

    def __iter__(self):
        for line in self.script:
            yield line

    def __str__(self):
        return '\n'.join(self.__iter__())