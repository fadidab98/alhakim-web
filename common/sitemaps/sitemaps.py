from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from accounts.models import Doctor


class DoctorSitemap(Sitemap):
    priority = 0.5
    protocol = "https"
    i18n = True

    def items(self):
        return Doctor.objects.all()

    def location(self, obj):
        return reverse("accounts:profile", args=[obj.id])


class IndexSitemap(Sitemap):
    protocol = "https"
    i18n = True

    def items(self):
        return ["base:index"]

    def location(self, item):
        return reverse(item)


class TermsSitemap(Sitemap):
    priority = 1.0
    protocol = "https"
    i18n = True

    def items(self):
        return ["base:terms"]

    def location(self, item):
        return reverse(item)


class PrivacySitemap(Sitemap):
    priority = 1.0
    protocol = "https"
    i18n = True

    def items(self):
        return ["base:privacy"]

    def location(self, item):
        return reverse(item)
