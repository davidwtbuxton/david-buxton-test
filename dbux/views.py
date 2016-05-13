
import logging
import os

from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from google.appengine.api import memcache
from google.appengine.ext import deferred

from . import utils


class HomeView(TemplateView):
    template_name = 'home.html'

home = HomeView.as_view()


class EnvView(TemplateView):
    template_name = 'env.html'

    def get_context_data(self, **kwargs):
        kwargs['env'] = sorted((k, v, repr(type(v))) for k, v in os.environ.items())
        kwargs['env_updated'] = timezone.now()
        kwargs['env_name'] = 'request'

        return super(EnvView, self).get_context_data(**kwargs)

env = EnvView.as_view()


class DeferredEnvView(TemplateView):
    template_name = 'env.html'

    def get_context_data(self, **kwargs):
        kwargs['env'] = memcache.get('deferred_env') or []
        kwargs['env_updated'] = memcache.get('deferred_env_updated')
        kwargs['env_name'] = 'deferred task'

        return super(DeferredEnvView, self).get_context_data(**kwargs)

deferred_env = DeferredEnvView.as_view()


class CronEnvView(TemplateView):
    template_name = 'env.html'

    def get_context_data(self, **kwargs):
        kwargs['env'] = memcache.get('cron_env') or []
        kwargs['env_updated'] = memcache.get('cron_env_updated')
        kwargs['env_name'] = 'cron task'

        return super(CronEnvView, self).get_context_data(**kwargs)

cron_env = CronEnvView.as_view()


def save_deferred_environment():
    env = tuple(sorted((str(k), str(v), repr(type(v))) for k, v in os.environ.items()))
    memcache.set('deferred_env', env)
    memcache.set('deferred_env_updated', timezone.now())

    return HttpResponse('OK')


def environment_task(request):
    env = tuple(sorted((str(k), str(v), repr(type(v))) for k, v in os.environ.items()))
    memcache.set('cron_env', env)
    memcache.set('cron_env_updated', timezone.now())

    deferred.defer(save_deferred_environment)

    return HttpResponse('OK')


@csrf_exempt
def deferred_handler(request):
    from google.appengine.ext.deferred.deferred import (
        run,
        SingularTaskFailure,
        PermanentTaskFailure
    )

    response = HttpResponse()

    if 'HTTP_X_APPENGINE_TASKEXECUTIONCOUNT' in request.META:
        logging.debug("[DEFERRED] Retry %s of deferred task", request.META['HTTP_X_APPENGINE_TASKEXECUTIONCOUNT'])

    if 'HTTP_X_APPENGINE_TASKNAME' not in request.META:
        logging.critical('Detected an attempted XSRF attack. The header "X-AppEngine-Taskname" was not set.')
        response.status_code = 403
        return response

    in_prod = utils.on_production()

    if in_prod and os.environ.get("REMOTE_ADDR") != "0.1.0.2":
        logging.critical('Detected an attempted XSRF attack. This request did not originate from Task Queue.')
        response.status_code = 403
        return response

    try:
        run(request.body)
    except SingularTaskFailure:
        logging.debug("Failure executing task, task retry forced")
        response.status_code = 408
    except PermanentTaskFailure:
        logging.exception("Permanent failure attempting to execute task")

    return response
