from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import FileSystemStorage
from django.http import Http404, JsonResponse
from django.views import generic
from django.views.generic.edit import FormMixin

from .forms import ComposeForm, FileForm
from .models import ChatMessage, Thread


class InboxView(LoginRequiredMixin, generic.ListView):
    template_name = 'chat/inbox.html'
    context_object_name = 'threads'

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)


class ThreadView(LoginRequiredMixin, FormMixin, generic.DetailView):
    template_name = 'chat/thread.html'
    form_class = ComposeForm
    success_url = './'

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        for msg in obj.chatmessage_set.all():
            if request.user != msg.user:
                if msg.read == False:
                    msg.read = True
                    msg.save()

        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

    def get_object(self):
        other_id = self.kwargs.get("id")
        obj, created = Thread.objects.get_or_new(self.request.user, other_id)
        if obj == None:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.get_form()
        context['file_form'] = FileForm()
        return context

    def post(self, request, *args, **kwargs):
        sender = request.user
        receiver = kwargs['id']

        thread = Thread.objects.get_or_new(sender, receiver)[0]

        message = request.POST['message']

        try:
            ChatMessage.objects.create(thread=thread, user=sender, message=message)
        except Exception as ex:
            print('err', ex)

        if sender.is_doctor and sender.profile_doctor.profile_pic:
            profile_pic = sender.profile_doctor.profile_pic.url
        else:
            profile_pic = '/static/images/user.webp/'

        return JsonResponse({'message': str(message), 'profile_pic': str(profile_pic)})


class UploadFile(LoginRequiredMixin, generic.View):
    def post(self, request, *args, **kwargs):
        sender = request.user
        receiver = kwargs['id']

        thread = Thread.objects.get_or_new(sender, receiver)[0]

        attached_file = request.FILES['file']

        file_instance = None

        try:
            file_instance = ChatMessage.objects.create(thread=thread, user=sender, attached_file=attached_file)
        except:
            pass

        if sender.is_doctor and sender.profile_doctor.profile_pic:
            profile_pic = sender.profile_doctor.profile_pic.url
        else:
            profile_pic = '/staticfiles/images/user'

        return JsonResponse({'fname': str(file_instance.filename()), 'link': file_instance.attached_file.url, 'profile_pic': str(profile_pic)})
