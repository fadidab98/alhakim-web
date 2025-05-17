from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django import forms
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from specialties.models import Specialty

from .models import Consultation, Document


class ConsultationForm(forms.ModelForm):
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        empty_label=_("-- لا أعرف الاختصاص المتعلق بمشكلتي --"),
        label=_("الاختصاص"),
        required=False,
    )
    doctor = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label=_("-- قم باختيار الاختصاص أولاً --"),
        label=_("الطبيب"),
        required=False,
    )
    symptoms = forms.CharField(
        required=False,
        label=_("الأعراض"),
        widget=forms.CheckboxSelectMultiple(
            choices=Consultation.SYMPTOMS.choices, attrs={"class": "form-check-input"}
        ),
    )
    reply_via = forms.CharField(
        label=_("الرد عبر"),
        widget=forms.CheckboxSelectMultiple(choices=Consultation.REPLY.choices, attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Consultation
        exclude = ("id", "patient", "read", "replied")

        labels = {
            "specialty": _("الاختصاص"),
            "doctor": _("الطبيب"),
            "problem": _("المشكلة الصحية"),
            "symptoms": _("الأعراض"),
            "problem_date": _("تاريخ بدء المشكلة"),
            "chronic_diseases": _("أمراض مزمنة"),
            "medicines": _("اﻷدوية المتناولة"),
            "allergy": _("حساسية"),
            "previous_surgeries": _("عمليات سابقة"),
            "reply_via": _("الرد على الطلب عبر"),
            "age": _("العمر"),
            "gender": _("الجنس"),
            "email": _("الإيميل"),
        }

        widgets = {
            "problem": forms.Textarea(attrs={"rows": 5}),
            "problem_date": forms.DateInput(attrs={"type": "date"}),
            "chronic_diseases": forms.Textarea(attrs={"rows": 3}),
            "medicines": forms.Textarea(attrs={"rows": 2}),
            "allergy": forms.Textarea(attrs={"rows": 2}),
            "previous_surgeries": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "consultation_form-specialty" in self.data:
            if self.data.get("consultation_form-specialty") != "-1":
                try:
                    specialty_id = int(self.data.get("consultation_form-specialty"))
                    specialty = Specialty.objects.get(id=specialty_id)
                    self.fields["doctor"].queryset = User.objects.filter(
                        is_doctor=True, profile_doctor__specialty=specialty
                    )
                except (ValueError, TypeError):
                    pass

            else:
                self.fields["doctor"].label = _("-- قم باختيار الاختصاص أولاً --")
                self.fields["doctor"].queryset = User.objects.none()


class DocumentsForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = [
            "document",
        ]

        labels = {"document": _("صور أشعة / تحاليل طبية")}

        widgets = {
            "document": forms.ClearableFileInput(attrs={"class": "form-control", "multiple": True}),
        }


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
