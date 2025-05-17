from cloudinary_storage.storage import RawMediaCloudinaryStorage
from common.validators.validate_file_size import validate_file_size
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _


class ThreadManager(models.Manager):
    def by_user(self, user):
        qlookup = Q(first=user) | Q(second=user)
        qlookup2 = Q(first=user) & Q(second=user)
        qs = self.get_queryset().filter(qlookup).exclude(qlookup2).distinct()
        return qs

    def get_or_new(self, user, other_id):
        id = user.id
        if id == other_id:
            return None
        qlookup1 = Q(first__id=id) & Q(second__id=other_id)
        qlookup2 = Q(first__id=other_id) & Q(second__id=id)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
        if qs.count() == 1:
            return qs.first(), False
        elif qs.count() > 1:
            return qs.order_by('timestamp').first(), False
        else:
            Klass = user.__class__
            user2 = Klass.objects.get(id=other_id)
            if user != user2:
                obj = self.model(
                        first=user, 
                        second=user2
                    )
                obj.save()
                return obj, True
            return None, False


class Thread(models.Model):
    first = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_first')
    second = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_thread_second')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    objects = ThreadManager()

    class Meta:
        ordering = ('timestamp',)


class ChatMessage(models.Model):
    thread = models.ForeignKey(Thread, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='sender', on_delete=models.CASCADE)

    message = models.TextField(null=True, blank=True)
    attached_file = models.FileField(upload_to='Chat/Files', validators=[validate_file_size], storage=RawMediaCloudinaryStorage())

    timestamp = models.DateTimeField(auto_now_add=True)

    read = models.BooleanField(default=False)

    def __str__(self):
        if self.message:
            return Truncator(str(self.message)).chars(50, html=True)
        else:
            return str(_('تم إرسال ملف'))
    
    def filename(self):
        if self.attached_file:
            return self.attached_file.name.split('/')[-1]
        else:
            return None
        
    class Meta:
        ordering = ('timestamp',)