from django.shortcuts import render
from django.views.generic import TemplateView

from .models import Performance


def index(request):
    return render(request, 'index.html', {})


class PanelView(TemplateView):
    template_name = "panel.html"

    def get_context_data(self, **kwargs):
        out = super().get_context_data(**kwargs)
        out.update({
            'upcomming': Performance.upcomming(),
            'count': Performance.objects.filter(state=Performance.STATE_DEMONSTRATED).count(),
        })
        return out

"""
- prave se promita
- pripraveno k promitani
- nedavno promitnute
"""
