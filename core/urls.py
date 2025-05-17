from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView, TemplateView

from accounts.views import LoadDoctors
from common.sitemaps import sitemaps

sitemaps = {
    "doctor": sitemaps.DoctorSitemap,
    "index": sitemaps.IndexSitemap,
    "privacy": sitemaps.PrivacySitemap,
    "terms": sitemaps.TermsSitemap,
}

urlpatterns = (
    [
        path(
            "sitemap.xml",
            sitemap,
            {"sitemaps": sitemaps},
            name="django.contrib.sitemaps.views.sitemap",
        ),
        path(
            "robots.txt",
            TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        ),
        path(
            "favicon.ico",
            RedirectView.as_view(url=staticfiles_storage.url("images/favicon.ico")),
        ),
        path("ads.txt", RedirectView.as_view(url=staticfiles_storage.url("ads.txt"))),
        path("i18n/", include("django.conf.urls.i18n")),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("base.urls", namespace="base")),
    path("ajax/load-doctors", LoadDoctors.as_view(), name="ajax_load_doctors"),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("chat/", include("chat.urls", namespace="chat")),
)
