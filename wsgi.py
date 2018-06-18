import datetime
import functools
import os
import re
import sys
# import urlparse

import bottle
# from google.appengine.api import memcache
# from google.appengine.api import urlfetch
# from google.appengine.ext import deferred


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


@app.route('/appengine-env', name='appengine_env')
@view('env.html')
def appengine_env():
    """This view just displays the env variables that were previously saved
    in memcache.
    """
    return {
        'env': (memcache.get('appengine_env') or []),
        'env_updated': memcache.get('appengine_env_updated'),
        'env_name': 'appengine request',
    }


@app.route('/tasks/appengine-env-trigger', name='appengine_env_trigger')
def appengine_env_trigger():
    """Make a request to the app itself with the urlfetch service, so that the
    X-Appengine-Inbound-Appid header is added to the request.
    """
    url = bottle.request.url
    url = urlparse.urljoin(url, bottle.url('appengine_env_save'))
    urlfetch.fetch(url, follow_redirects=False)

    return 'OK'


@app.route('/tasks/appengine-env-save', name='appengine_env_save')
def appengine_env_save():
    """Save the request environment. The request must have the special
    X-Appengine-Inbound-Appid header.
    """
    if 'HTTP_X_APPENGINE_INBOUND_APPID' in os.environ:
        env = format_env()
        memcache.set('appengine_env', env)
        memcache.set('appengine_env_updated', datetime.datetime.utcnow())

    return 'OK'


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
