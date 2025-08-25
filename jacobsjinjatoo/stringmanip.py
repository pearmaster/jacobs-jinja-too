import stringcase

def bold(s: str):
    if s and s is not None and s != 'None' and len(s) > 0:
        return "**%s**" % (s)
    else:
        return ''

def italics(s: str):
    if s and s is not None and s != 'None' and len(s) > 0:
        return "_%s_" % (s)
    else:
        return ''

def upper_camel_case(s: str):
    return stringcase.pascalcase(stringcase.snakecase(s)).replace('_', '')

def lower_camel_case(s: str):
    return stringcase.camelcase(stringcase.snakecase(s)).replace('_', '')