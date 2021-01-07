import re


def extract_app_name(name):
    if re.match('(.* ([a-z]|[0-9]){10})', name):
        app_name = ' '.join(name.split(' ')[:-1])
    else:
        app_name = name

    return app_name