import sys

from google.appengine.ext import ndb


class Config(ndb.Model):
    secret_key = ndb.StringProperty()


def get_config():
    from django.utils import crypto

    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = crypto.get_random_string(50, chars)

    return Config.get_or_insert('global_config', secret_key=secret_key)


def setup():
    if 'libs' not in sys.path:
        sys.path.insert(1, 'libs')
