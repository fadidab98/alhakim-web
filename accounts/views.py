import cloudinary.uploader
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetConfirmView
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views import generic

from common.middleware.permissions import DoctorUserOnlyMixin, SuperUserOnlyMixin
from specialties.models import Specialty

from .forms import (
    CreateDoctorForm,
    CreatePatientForm,
    CreateUserForm,
    DoctorDeleteForm,
    PasswordResetForm,
    UpdateDoctorForm,
    UpdatePatientForm,
    UpdateUserForm,
)
from .models import Doctor, User


class UserLogin(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        if not self.request.GET.get("next"):
            if self.request.user.is_doctor:
                return reverse_lazy("accounts:profile", kwargs={"id": self.request.user.id})
            else:
                return reverse_lazy("base:consult")
        else:
            return super().get_success_url()

    def form_invalid(self, form):
        if form.cleaned_data["username"] == "invalid" or form.cleaned_data["username"] == "letters":
            messages.error(self.request, _("رقم الهاتف الذي أدخلته خاطئ!"))
        else:
            messages.error(self.request, _("معلومات الحساب التي أدخلتها خاطئة!"))
        return super().form_invalid(form)


class UserLogout(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy("base:index")


class RegisterDoctor(generic.TemplateView):
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:register_doctor")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_form"] = CreateUserForm(prefix="user_form", doctor=True)
        context["profile_form"] = CreateDoctorForm(prefix="profile_form")

        return context

    def post(self, request, *args, **kwargs):
        user_form = CreateUserForm(request.POST or None, prefix="user_form")
        profile_form = CreateDoctorForm(request.POST or None, request.FILES, prefix="profile_form")

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_doctor = True
            user.phone = user_form.cleaned_data["full_phone"]

            try:
                user.save()
            except IntegrityError:
                user_form.add_error("full_phone", _("هذا الرقم مأخوذ سابقا, الرجاء استخدام رقم اخر"))
                context = {"user_form": user_form, "profile_form": profile_form}
                return render(request, "accounts/register.html", context)

            doctor = profile_form.save(commit=False)
            doctor.user = user
            doctor.save()

            messages.success(request, _("تم إرسال طلب إنشاء حساب جديد. الرجاء الانتظار حتى نقبل طلبك!"))

            return redirect(reverse_lazy("accounts:register_doctor"))
        else:
            context = {"user_form": user_form, "profile_form": profile_form}
            return render(request, "accounts/register.html", context)


class DoctorProfile(generic.DetailView):
    template_name = "accounts/profile.html"

    def get_object(self):
        return get_object_or_404(Doctor, user__id=self.kwargs["id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            countryEN, countryAR = self.get_object().country.split("-")
            context["countryEN"] = countryEN
            context["countryAR"] = countryAR
        except:
            pass

        return context


class UpdateDoctor(LoginRequiredMixin, DoctorUserOnlyMixin, generic.TemplateView):
    template_name = "accounts/update.html"

    def get_object(self):
        user = self.request.user
        profile = self.request.user.profile_doctor

        return {"user": user, "profile": profile}

    def get(self, request, *args, **kwargs):
        if request.user.id == self.get_object().get("user").id:
            return super().get(request, *args, **kwargs)
        else:
            return redirect(reverse_lazy("base:index"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_form"] = UpdateUserForm(prefix="user_form", instance=self.get_object().get("user"))
        context["profile_form"] = UpdateDoctorForm(prefix="profile_form", instance=self.get_object().get("profile"))
        context["specialty"] = self.get_object().get("profile").specialty
        context["phone"] = self.get_object().get("user").phone

        try:
            countryEN, countryAR = self.get_object()["profile"].country.split("-")
            country = self.get_object()["profile"].country
            context["countryEN"] = countryEN
            context["countryAR"] = countryAR
            context["country"] = country
        except:
            pass

        return context

    def post(self, request, *args, **kwargs):
        user_form = UpdateUserForm(request.POST, instance=self.get_object().get("user"), prefix="user_form")
        profile_form = UpdateDoctorForm(
            request.POST, request.FILES, instance=self.get_object().get("profile"), prefix="profile_form"
        )

        if user_form.is_valid() and profile_form.is_valid():
            if "profile_pic" in profile_form.changed_data:
                cloudinary.uploader.destroy(Doctor.objects.get(user=request.user).profile_pic.name, invalidate=True)

            if "syndicate_card" in profile_form.changed_data:
                cloudinary.uploader.destroy(Doctor.objects.get(user=request.user).syndicate_card.name, invalidate=True)

            if "cv" in profile_form.changed_data:
                cloudinary.uploader.destroy(Doctor.objects.get(user=request.user).cv.name, invalidate=True)

            user = user_form.save(commit=False)

            if user_form.cleaned_data["new_password"]:
                user.set_password(user_form.cleaned_data["new_password"])

            user.phone = user_form.cleaned_data["full_phone"]

            try:
                user.save()
            except IntegrityError:
                user_form.add_error("full_phone", _("هذا الرقم مأخوذ سابقا, الرجاء استخدام رقم اخر"))
                context = {"user_form": user_form, "profile_form": profile_form}
                return render(request, "accounts/register.html", context)

            profile_form.save()

            messages.success(self.request, _("تم تعديل حسابك بنجاح!"))

            return redirect(reverse_lazy("accounts:update_doctor", kwargs={"id": self.get_object().get("user").id}))
        else:
            context = {"user_form": user_form, "profile_form": profile_form}
            return render(request, "accounts/update.html", context)


class DeleteDoctor(LoginRequiredMixin, SuperUserOnlyMixin, generic.FormView):
    template_name = "accounts/delete_doctor.html"
    form_class = DoctorDeleteForm

    def form_valid(self, form):
        doctor = form.cleaned_data["doctor"]
        cloudinary.uploader.destroy(doctor.profile_doctor.profile_pic.name, invalidate=True)
        cloudinary.uploader.destroy(doctor.profile_doctor.syndicate_card.name, invalidate=True)
        cloudinary.uploader.destroy(doctor.profile_doctor.cv.name, invalidate=True)
        doctor.delete()
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, _("تم حذف حساب الطبيب بنجاح!"))

        return reverse_lazy("accounts:delete_doctor")


class LoadDoctors(generic.TemplateView):
    def get(self, request):
        specialty_id = request.GET["specialty_id"]

        if specialty_id == "-1":
            doctors = None
        else:
            specialty = Specialty.objects.get(id=specialty_id)

            doctors = User.objects.filter(
                is_doctor=True, is_active=True, profile_doctor__specialty=specialty
            ).order_by("?")

        return render(request, "accounts/doctor_dropdown_list.html", {"doctors": doctors})


class RegisterPatient(generic.TemplateView):
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:register")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_form"] = CreateUserForm(prefix="user_form")
        context["profile_form"] = CreatePatientForm(prefix="profile_form")
        context["u_type"] = "patient"

        return context

    def post(self, request, *args, **kwargs):
        user_form = CreateUserForm(request.POST, prefix="user_form")
        profile_form = CreatePatientForm(request.POST, prefix="profile_form")

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.is_patient = True
            user.is_active = True
            user.phone = user_form.cleaned_data["full_phone"]

            try:
                user.save()
            except IntegrityError:
                user_form.add_error("full_phone", _("هذا الرقم مأخوذ سابقا, الرجاء استخدام رقم اخر"))
                context = {"user_form": user_form, "profile_form": profile_form}
                return render(request, "accounts/register.html", context)

            patient = profile_form.save(commit=False)
            patient.user = user
            patient.save()

            messages.success(request, _("تم إنشاء حساب جديد!"))

            reg_user = authenticate(
                phone=user_form.cleaned_data["full_phone"], password=user_form.cleaned_data["password1"]
            )

            if reg_user is not None:
                login(request, reg_user)
                return redirect(reverse_lazy("base:consult"))
        else:
            context = {"user_form": user_form, "profile_form": profile_form}
            return render(request, "accounts/register.html", context)


class UpdatePatient(LoginRequiredMixin, generic.TemplateView):
    template_name = "accounts/update.html"

    def get_object(self):
        user = self.request.user
        profile = self.request.user.profile_patient

        return {"user": user, "profile": profile}

    def get(self, request, *args, **kwargs):
        if request.user.id == self.get_object().get("user").id:
            return super().get(request, *args, **kwargs)
        else:
            return redirect(reverse_lazy("base:index"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["user_form"] = UpdateUserForm(prefix="user_form", instance=self.get_object().get("user"))
        context["profile_form"] = UpdatePatientForm(prefix="profile_form", instance=self.get_object().get("profile"))
        context["phone"] = self.get_object().get("user").phone

        return context

    def post(self, request, *args, **kwargs):
        user_form = UpdateUserForm(request.POST, instance=self.get_object().get("user"), prefix="user_form")
        profile_form = UpdatePatientForm(
            request.POST, instance=self.get_object().get("profile"), prefix="profile_form"
        )

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)

            if user_form.cleaned_data["new_password"]:
                user.set_password(user_form.cleaned_data["new_password"])

            user.phone = user_form.cleaned_data["full_phone"]

            try:
                user.save()
            except IntegrityError:
                user_form.add_error("full_phone", _("هذا الرقم مأخوذ سابقا, الرجاء استخدام رقم اخر"))
                context = {"user_form": user_form, "profile_form": profile_form}
                return render(request, "accounts/register.html", context)

            profile_form.save()

            messages.success(self.request, _("تم تعديل حسابك بنجاح!"))

            return redirect(reverse_lazy("accounts:update_patient", kwargs={"id": self.get_object().get("user").id}))
        else:
            context = {"user_form": user_form, "profile_form": profile_form}
            return render(request, "accounts/update.html", context)


class PhonePasswordResetView(generic.FormView):
    template_name = "accounts/password_reset.html"
    success_url = reverse_lazy("accounts:password_reset_done")
    form_class = PasswordResetForm

    def form_valid(self, form):
        phone = form.cleaned_data["phone"]
        email = form.cleaned_data["email"]

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return super().form_invalid(form)

        token_generator = default_token_generator
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        reset_url = self.request.build_absolute_uri(
            reverse("accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )

        send_mail(
            _("إعادة تعيين كلمة المرور"),
            reset_url,
            settings.EMAIL_HOST_USER,
            [
                email,
            ],
            fail_silently=False,
        )

        return super().form_valid(form)


class PhonePasswordResetDoneView(generic.TemplateView):
    template_name = "accounts/password_reset_done.html"


class PhonePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"

    def get_user(self, uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64).decode("utf-8")
            user = User.objects.get(id=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    def form_valid(self, form):
        user = form.save()

        authenticate(user)

        login(self.request, user)

        return redirect(reverse("base:consult"))
