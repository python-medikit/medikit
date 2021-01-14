def which(cmd, *more_cmds):
    return (
        "$(shell "
        + " || ".join(
            (
                "which {cmd}".format(cmd=cmd),
                *("which {cmd}".format(cmd=more_cmd) for more_cmd in more_cmds),
                "echo {cmd}".format(cmd=cmd),
            )
        )
        + ")"
    )
