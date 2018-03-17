from medikit.feature import Feature


class MakeConfig(Feature.Config):
    on_generate = 'medikit.feature.make.on_generate'
    """Happens during the makefile generation."""

    def __init__(self):
        self.include_medikit_targets = True
        self.extras = {'dev'}

    def disable_medikit_targets(self):
        self.include_medikit_targets = False