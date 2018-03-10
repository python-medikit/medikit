from medikit import steps


def setup_default_pipelines(config):
    # todo, move this in a configurable place
    with config.pipeline('release') as release:
        release.add(steps.Install())
        release.add(steps.BumpVersion())
        release.add(steps.Make('update-requirements'))
        release.add(steps.Make('clean install'))  # test docs
        release.add(steps.System('git add -p .', interractive=True))
        release.add(steps.Commit('Release: {version}', tag=True))
