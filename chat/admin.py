from django.contrib import admin

from .models import ChatMessage, Thread

admin.site.register(Thread)
admin.site.register(ChatMessage)