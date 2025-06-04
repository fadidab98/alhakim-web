import cloudinary.uploader
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage, send_mail
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from django.views import generic

from accounts.models import Doctor
from chat.models import Thread
from common.middleware.permissions import DoctorUserOnlyMixin
from specialties.models import Specialty

from .forms import ConsultationForm, ContactForm, DocumentsForm
from .models import Consultation, ConsultationHistory, Document


class Index(generic.ListView):
    model = Doctor
    context_object_name = "doctors"
    template_name = "base/index.html"
    queryset = Doctor.objects.filter(user__is_active=True, user__is_superuser=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["doctors_count"] = Doctor.objects.filter(
            user__is_superuser=False, user__is_active=True
        ).count()
        context["specialty_count"] = Specialty.objects.count()
        context["consultation_count"] = int(Consultation.objects.count()) * 2
        context["form"] = ContactForm()

        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)

        if form.is_valid():
            subject = "Contact Form Message"

            name = request.POST["name"]
            email = request.POST["email"]
            message = request.POST["message"]

            body = f"Email From {name} - {email}: \n \n {message}"

            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER,
                [
                    "berrofouad66@gmail.com",
                ],
                fail_silently=False,
            )

            html_message = render_to_string(
                "base/contact_reply.html",
                {
                    "link_en": request.build_absolute_uri("/en/consult/"),
                    "link_ar": request.build_absolute_uri("/ar/consult/"),
                },
            )
            plain_message = strip_tags(html_message)

            send_mail(
                _("أهلا وسهلا بك في موقعنا"),
                plain_message,
                settings.EMAIL_HOST_USER,
                [
                    email,
                ],
                fail_silently=False,
            )

            return redirect(reverse_lazy("base:index"))

        else:
            context = {}
            context["doctors_count"] = Doctor.objects.filter(
                user__is_superuser=False, user__is_active=True
            ).count()
            context["specialty_count"] = Specialty.objects.count()
            context["consultation_count"] = int(Consultation.objects.count()) * 2
            context["form"] = ContactForm(request.POST)
            return render(request, "base/index.html", context)


class Privacy(generic.TemplateView):
    template_name = "base/privacy.html"


class Terms(generic.TemplateView):
    template_name = "base/terms.html"


class Rules(generic.TemplateView):
    template_name = "base/rules.html"


class Consult(LoginRequiredMixin, generic.TemplateView):
    template_name = "base/consult.html"
    success_url = reverse_lazy("base:consult")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["consultation_form"] = ConsultationForm(prefix="consultation_form")
        context["documents_form"] = DocumentsForm(prefix="documents_form")
        return context

    def post(self, request, *args, **kwargs):
        consultation_form = ConsultationForm(request.POST, prefix="consultation_form")
        documents_form = DocumentsForm(request.POST, request.FILES, prefix="documents_form")

        if consultation_form.is_valid() and documents_form.is_valid():
            with transaction.atomic():
                try:
                    consultation = consultation_form.save(commit=False)
                    consultation.specialty = consultation_form.cleaned_data.get(
                        "specialty", None
                    )
                    consultation.doctor = consultation_form.cleaned_data.get("doctor", None)
                    consultation.patient = request.user
                    consultation.save()

                    for f in request.FILES.getlist("documents_form-document"):
                        Document(consultation=consultation, document=f).save()

                    if consultation.doctor is not None:
                        ConsultationHistory.objects.create(
                            patient=consultation.patient, doctor=consultation.doctor
                        )

                    messages.success(request, _("تم إرسال الطلب بنجاح!"))
                    return redirect(reverse_lazy("base:consult"))

                except Exception as ex:
                    print(ex)  # Exception is printed to console
                    transaction.set_rollback(True)
                    messages.error(request, _("حدث خطأ أثناء معالجة الطلب."))
        else:
            messages.error(request, _("حدث خطأ في استمارة الاستشارة."))

        context = {
            "consultation_form": consultation_form,
            "documents_form": documents_form,
        }
        return render(request, "base/consult.html", context)


class RequestsList(LoginRequiredMixin, DoctorUserOnlyMixin, generic.ListView):
    model = Consultation
    template_name = "base/requests_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        queryset = Consultation.objects.filter(doctor=self.request.user)

        return queryset


class UnknownRequestsList(LoginRequiredMixin, DoctorUserOnlyMixin, generic.ListView):
    model = Consultation
    template_name = "base/requests_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        queryset = Consultation.objects.filter(Q(doctor=None) | Q(specialty=None))

        return queryset


class RequestsHistory(LoginRequiredMixin, DoctorUserOnlyMixin, generic.ListView):
    model = ConsultationHistory
    template_name = "base/history.html"
    context_object_name = "messages"

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = ConsultationHistory.objects.order_by("-created")
        else:
            queryset = ConsultationHistory.objects.filter(doctor=self.request.user).order_by(
                "-created"
            )

        return queryset


class RequestDetails(LoginRequiredMixin, DoctorUserOnlyMixin, generic.DetailView):
    model = Consultation
    template_name = "base/request_details.html"
    context_object_name = "request"

    def get_object(self):
        return get_object_or_404(Consultation, id=self.kwargs["id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["documents"] = Document.objects.filter(consultation=self.get_object())

        if self.get_object().symptoms:
            SYMPTOMS_CATEGORIES = dict(Consultation.SYMPTOMS.choices)
            symptoms = []
            for symptom in list(self.get_object().symptoms.split(",")):
                symptoms.append(
                    SYMPTOMS_CATEGORIES[
                        symptom.replace("'", "").replace("[", "").replace("]", "").strip()
                    ]
                )

            context["symptoms"] = symptoms

        reply_via = []

        for r in list(self.get_object().reply_via.split(",")):
            r = r.replace("[", "").replace("'", "").replace("]", "").strip()
            reply_via.append(r)

        c = Consultation.objects.get(id=self.get_object().id)
        c.read = True
        c.save()

        context["reply_via"] = reply_via

        return context

    def post(self, request, *args, **kwargs):
        if "email_reply" in request.POST:
            body = request.POST.get("body")
            files = request.FILES.getlist("attachment")
            subject = f"Email From {request.user.name_en}"

            try:
                mail = EmailMessage(
                    subject,
                    body,
                    settings.EMAIL_HOST_USER,
                    [
                        self.get_object().email,
                    ],
                )
                for f in files:
                    mail.attach(f.name, f.read(), f.content_type)
                mail.send()

            except Exception:
                messages.error(request, _("حصلت مشكلة أثناء الإرسال, الرجاء المحاولة لاحقاً"))
                return redirect(
                    reverse_lazy("base:request_details", kwargs={"id": self.get_object().id})
                )

            messages.success(request, _("تم إرسال الإيميل بنجاح!"))

        else:
            print("other")

        c = Consultation.objects.get(id=self.get_object().id)
        c.replied = True
        c.save()

        return redirect(
            reverse_lazy("base:request_details", kwargs={"id": self.get_object().id})
        )


class WhatsappReply(LoginRequiredMixin, DoctorUserOnlyMixin, generic.RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        consultation = Consultation.objects.get(id=kwargs["id"])
        consultation.replied = True
        consultation.save()

        if kwargs["device"] == "mobile":
            return f"https://api.whatsapp.com/send?phone={kwargs['number']}"
        elif kwargs["device"] == "pc":
            return f"https://web.whatsapp.com/send?phone={kwargs['number']}"
        else:
            return HttpResponseBadRequest()


class DirectReply(LoginRequiredMixin, DoctorUserOnlyMixin, generic.RedirectView):
    permanent = False

    def get_redirect_url(self, **kwargs):
        thread = Thread.objects.get_or_new(self.request.user, kwargs["id"])[0]
        return reverse_lazy("chat:thread_messages", kwargs={"id": thread.second.id})


class RequestDelete(LoginRequiredMixin, DoctorUserOnlyMixin, generic.DeleteView):
    model = Consultation

    def get_object(self):
        return get_object_or_404(Consultation, id=self.kwargs["id"])

    def post(self, request, *args, **kwargs):
        for document in Document.objects.filter(consultation__id=self.get_object().id):
            cloudinary.uploader.destroy(document.name, invalidate=True)

        self.get_object().delete()

        return redirect(
            self.request.GET.get("prev")
            if self.request.GET.get("prev")
            else reverse_lazy("base:index")
        )
