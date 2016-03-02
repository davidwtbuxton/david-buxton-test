import os
import sys

from django.http import HttpResponse
from django.views.generic import TemplateView, View


class HomeView(TemplateView):
    template_name = 'home.html'

home = HomeView.as_view()


class EnvView(TemplateView):
    template_name = 'env.html'

    def get_context_data(self, **kwargs):
        kwargs['env'] = sorted((k, v, repr(type(v))) for k, v in os.environ.items())
        return super(EnvView, self).get_context_data(**kwargs)

env = EnvView.as_view()
