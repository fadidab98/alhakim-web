from django.contrib import admin

from .models import Consultation, Document, ConsultationHistory

admin.site.register(Consultation)
admin.site.register(Document)
admin.site.register(ConsultationHistory)