def get_divider(line):
    separators = {
        '; ',
        ': ',
        ', ',
        '| ',
        ' | ',
        '||',
        ';',
        ':',
        '  '
    }
    for sep in separators:
        if line.find(sep) >= 0:
            return sep
    else:
        return None
