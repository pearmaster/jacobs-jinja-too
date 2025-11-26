
def tokenize(s: str) -> list[str]:
    """
    Splits the input string `s` into tokens at these points:
        - Whitespace characters
        - These punctuation characters: `.`, `-`, and `_`
        - anywhere the case changes from lower to upper.

    Examples:
        "HelloWorld" -> ["Hello", "World"]
        "hello_world" -> ["hello", "world"]
        "ThisIsA-Test.String" -> ["This", "Is", "A", "Test", "String"]
     """
    import re
    if not s:
        return []
    # Split on whitespace, `.`, `-`, `_`, and case changes (lower→upper)
    # The pattern matches word boundaries created by these delimiters or case changes
    # Split also at transitions from digit to uppercase (e.g., Version2Update -> Version2, Update)
    tokens = re.split(r'[\s.\-_]+|(?<=[a-z0-9])(?=[A-Z])', s)
    # Filter out empty strings from the split
    return [token for token in tokens if token]

def bold(s: str) -> str:
    if s and s is not None and s != 'None' and len(s) > 0:
        return "**%s**" % (s)
    else:
        return ''

def italics(s: str):
    if s and s is not None and s != 'None' and len(s) > 0:
        return "_%s_" % (s)
    else:
        return ''

def upper_camel_case(s: str) -> str:
    tokens = tokenize(s)
    capitalized_tokens = [token.capitalize() for token in tokens]
    return ''.join(capitalized_tokens)

def lower_camel_case(s: str) -> str:
    """ Convert a string to lowerCamelCase, which is camel case starting with a lowercase letter."""
    tokens = tokenize(s)
    if not tokens:
        return ''
    first_token = tokens[0].lower()
    capitalized_tokens = [token.capitalize() for token in tokens[1:]]
    return first_token + ''.join(capitalized_tokens)

def lower_only(s: str) -> str:
    """ Converting a string to lowercasewithoutanyseparators.
    """
    tokens = tokenize(s)
    lower_tokens = [token.lower() for token in tokens]
    return ''.join(lower_tokens)

def hyphen_case(s: str) -> str:
    """ Converting a string to hyphen-case (lowercase with hyphens).
    """
    tokens = tokenize(s)
    lower_tokens = [token.lower() for token in tokens]
    return '-'.join(lower_tokens)

def path_case(s: str) -> str:
    """ Converting a string to path/case (lowercase with slashes).
    """
    tokens = tokenize(s)
    lower_tokens = [token.lower() for token in tokens]
    return '/'.join(lower_tokens)

def const_case(s: str) -> str:
    """ Converting a string to CONSTANT_CASE (uppercase with underscores).
    """
    tokens = tokenize(s)
    upper_tokens = [token.upper() for token in tokens]
    return '_'.join(upper_tokens)

def snake_case(s: str) -> str:
    """ Converting a string to snake_case (lowercase with underscores).
    """
    tokens = tokenize(s)
    lower_tokens = [token.lower() for token in tokens]
    return '_'.join(lower_tokens)

def commentblock(s: str, marker: str = '#') -> str:
    """Prefix each non-empty line in `s` with `marker`.

    - Preserves existing newline characters.
    - Works with single-line and multi-line strings.
    - If `s` is falsy, returns an empty string.
    """
    if s is None:
        return ''
    text = str(s)
    # Keep trailing newline if present
    has_trailing_newline = text.endswith('\n')
    lines = text.split('\n')
    # If the original ended with a newline, split will give an extra empty string at the end;
    # we want to preserve that behavior when joining back.
    prefixed = [f"{marker}{line}" if line != '' else marker for line in lines]
    result = "\n".join(prefixed)
    if not has_trailing_newline and result.endswith('\n'):
        result = result[:-1]
    return result

