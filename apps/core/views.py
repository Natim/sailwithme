from django.views.generic import TemplateView

from apps.listings.iso_weeks import SEASON_SHORTCUTS
from apps.listings.models import Port, RoutePage


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["season_shortcuts"] = [
            {"key": k, **v} for k, v in SEASON_SHORTCUTS.items()
        ]
        ctx["route_pages"] = RoutePage.objects.all()[:6]
        ctx["ports"] = Port.objects.all()[:200]
        return ctx
