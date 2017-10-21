import keyword
import textwrap
import tokenize


def is_identifier(ident):
    """Determines, if string is valid Python identifier."""

    # Smoke test — if it's not string, then it's not identifier, but we don't
    # want to just silence exception. It's better to fail fast.
    if not isinstance(ident, str):
        raise TypeError('expected str, but got {!r}'.format(type(ident)))

    # Quick test — if string is in keyword list, it's definitely not an ident.
    if keyword.iskeyword(ident):
        return False

    readline = (lambda: (yield ident.encode('utf-8-sig')))().__next__
    tokens = list(tokenize.tokenize(readline))

    # You should get exactly 3 tokens
    if len(tokens) != 3:
        return False

    # First one is ENCODING, it's always utf-8 because we explicitly passed in
    # UTF-8 BOM with ident.
    if tokens[0].type != tokenize.ENCODING:
        return False

    # Second is NAME, identifier.
    if tokens[1].type != tokenize.NAME:
        return False

    # Name should span all the string, so there would be no whitespace.
    if ident != tokens[1].string:
        return False

    # Third is ENDMARKER, ending stream
    if tokens[2].type != tokenize.ENDMARKER:
        return False

    return True


def format_file_content(s):
    return textwrap.dedent(s).strip() + '\n'