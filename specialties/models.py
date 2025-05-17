from django.db import models
from django.utils.translation import get_language

from common.utils.create_slug import create_slug

class Specialty(models.Model):
    name_en = models.CharField(max_length=70, unique=True)
    name_ar = models.CharField(max_length=70, unique=True)

    slug = models.SlugField(blank=True)

    def __str__(self):
        return self.name_en if get_language() == 'en' else self.name_ar
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = create_slug(self.__class__, self.name_en)

        return super().save(*args, **kwargs)
    
    class Meta:
        ordering = ('name_en',)