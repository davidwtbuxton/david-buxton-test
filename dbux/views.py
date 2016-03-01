import sys

from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        kwargs['env'] = [
            ('sys.stdout.encoding', sys.stdout.encoding),
        ]
        return super(HomeView, self).get_context_data(**kwargs)

home = HomeView.as_view()
