import datetime
import functools
import logging
import os

import bottle
from google.appengine.api import memcache
from google.appengine.ext import deferred


bottle.debug(True)
view = functools.partial(bottle.jinja2_view, template_lookup=['templates'])
app = bottle.default_app()


bottle.Jinja2Template.settings = {'autoescape': True}
bottle.Jinja2Template.defaults = {'url': bottle.url}


@app.route('/', name='home')
@view('home.html')
def home():
    return {}


@app.route('/env', name='env')
@view('env.html')
def env():
    return {
        'env': sorted((k, v, repr(type(v))) for k, v in os.environ.items()),
        'env_updated': datetime.datetime.now(),
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
    env = tuple(sorted((str(k), str(v), repr(type(v))) for k, v in os.environ.items()))
    memcache.set('cron_env', env)
    memcache.set('cron_env_updated', datetime.datetime.now())

    deferred.defer(save_deferred_environment)

    return 'OK'


def save_deferred_environment():
    env = tuple(sorted((str(k), str(v), repr(type(v))) for k, v in os.environ.items()))
    memcache.set('deferred_env', env)
    memcache.set('deferred_env_updated', datetime.datetime.now())

    return 'OK'
