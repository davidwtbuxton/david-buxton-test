from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^env$', views.env, name='env'),
]
