def which(cmd):
    return '$(shell which {cmd} || echo {cmd})'.format(cmd=cmd)