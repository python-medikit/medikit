from __future__ import absolute_import

import textwrap


def format_file_content(s):
    return textwrap.dedent(s).strip() + '\n'
