import datetime
import functools
import logging
import os
import re
import sys

import bottle
from google.appengine.api import memcache
from google.appengine.ext import deferred


bottle.debug(True)
view = functools.partial(bottle.jinja2_view, template_lookup=['templates'])
app = bottle.default_app()


bottle.Jinja2Template.settings = {'autoescape': True}
bottle.Jinja2Template.defaults = {'url': bottle.url}


def format_env():
    """Returns a sorted tuple of the environment dictionary, and in theory
    with memory addresses anonymised.
    """
    # Trying to find things that look like a memory address.
    pattern = re.compile(r'0x[0-9a-f]{8,}')
    anon_address = '0x12345678'
    env = ((str(k), str(v), repr(type(v))) for k, v in os.environ.items())
    clean_env = []

    for key, value, kind in env:
        value = pattern.sub(anon_address, value)
        kind = pattern.sub(anon_address, kind)
        clean_env.append((key, value, kind))

    return tuple(sorted(clean_env))


@app.route('/', name='home')
@view('home.html')
def home():
    return {}


@app.route('/python-path', name='python_path')
@view('python_path.html')
def python_path():
    return {
        'env_name': 'Python import path',
        'paths': sys.path,
    }


@app.route('/env', name='env')
@view('env.html')
def env():
    return {
        'env': format_env(),
        'env_updated': datetime.datetime.utcnow(),
        'env_name': 'request',
    }


@app.route('/deferred-env', name='deferred_env')
@view('env.html')
def deferred_env():
    return {
        'env': (memcache.get('deferred_env') or []),
        'env_updated': memcache.get('deferred_env_updated'),
        'env_name': 'deferred task',
    }


@app.route('/cron-env', name='cron_env')
@view('env.html')
def cron_env():
    return {
        'env': (memcache.get('cron_env') or []),
        'env_updated': memcache.get('cron_env_updated'),
        'env_name': 'cron task',
    }


@app.route('/tasks/environment')
def environment_task():
    env = format_env()
    memcache.set('cron_env', env)
    memcache.set('cron_env_updated', datetime.datetime.utcnow())

    deferred.defer(save_deferred_environment)

    return 'OK'


def save_deferred_environment():
    env = format_env()
    memcache.set('deferred_env', env)
    memcache.set('deferred_env_updated', datetime.datetime.utcnow())

    return 'OK'
