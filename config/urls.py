from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.i18n import set_language

from apps.core.views import HomeView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/setlang/", set_language, name="set_language"),
    path("accounts/", include("allauth.urls")),
    path("", HomeView.as_view(), name="home"),
    path("legal/cgu/", TemplateView.as_view(template_name="legal/cgu.html"), name="cgu"),
    path("profiles/", include("apps.profiles.urls")),
    path("boats/", include("apps.boats.urls")),
    path("listings/", include("apps.listings.urls")),
    path("messages/", include("apps.messaging.urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("billing/", include("apps.billing.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
