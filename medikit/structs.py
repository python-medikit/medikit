import textwrap


class Script(object):
    """
    Simple structure to hold a shell script for various usage, mainly to use in make targets.

    The goal is to make it flexible, as in alow the user to ammend it after definition.

    """

    def __init__(self, script=None):
        self.set(script)

    def set(self, script=None):
        self.script = self.parse_script(script)

    def prepend(self, script=None):
        """
        Prepend a script to the current script.

        :param script:
        """
        self.script = self.parse_script(script) + self.script

    def append(self, script=None):
        """
        Append a script to the current script.

        :param script:
        """
        self.script = self.script + self.parse_script(script)

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
