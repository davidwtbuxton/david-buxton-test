import os


def on_production():
    return not os.environ.get('SERVER_SOFTWARE', 'Development').startswith('Development')
