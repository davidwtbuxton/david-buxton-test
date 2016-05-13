from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^_ah/queue/deferred$', views.deferred_handler, name='deferred_handler'),
    url(r'^$', views.home, name='home'),
    url(r'^env$', views.env, name='env'),
    url(r'^deferred-env$', views.deferred_env, name='deferred_env'),
    url(r'^cron-env$', views.cron_env, name='cron_env'),

    url(r'^tasks/environment-task', views.environment_task, name='environment_task'),
]
