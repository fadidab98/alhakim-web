import uuid

from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from common.validators.validate_file_size import validate_file_size
from specialties.models import Specialty


class Consultation(models.Model):
    class SYMPTOMS(models.TextChoices):
        Pain = "Pain", _("ألم")
        Fever = "Fever", _("حرارة")
        Headache = "Headache", _("صداع")
        Inflation = "Inflation", _("تورم")
        Vertigo = "Vertigo", _("دوار")
        Vomiting = "Vomiting", _("تقيأ")
        Diarrhea = "Diarrhea", _("إسهال")
        Constipation = "Constipation", _("إمساك")
        BreathingDifficulty = "BreathingDifficulty", _("صعوبة التنفس")

    class REPLY(models.TextChoices):
        Email = "Email", _("الإيميل")
        Whatsapp = "Whatsapp", _("الواتساب")
        Telegram = "Telegram", _("تيليغرام")
        Direct = "Direct", _("مباشرة (من خلال هذا الموقع)")

    class GENDER(models.TextChoices):
        MALE = "MALE", _("Male")
        FEMALE = "FEMALE", _("Female")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)

    patient = models.ForeignKey(
        User,
        related_name="consultation_patient",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    doctor = models.ForeignKey(
        User,
        related_name="consultation_doctor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    gender = models.CharField(max_length=15, choices=GENDER.choices, null=True)
    age = models.PositiveIntegerField(null=True)

    email = models.EmailField(null=True, blank=True)

    problem = models.TextField()
    symptoms = models.CharField(max_length=225, null=True, blank=True)
    problem_date = models.DateField()
    chronic_diseases = models.TextField(null=True, blank=True)
    medicines = models.TextField(null=True, blank=True)
    allergy = models.TextField(null=True, blank=True)
    previous_surgeries = models.TextField(null=True, blank=True)
    reply_via = models.CharField(max_length=225)

    created = models.DateTimeField(auto_now_add=True)

    read = models.BooleanField(default=False)
    replied = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        try:
            if self.doctor:
                return f"{self.patient.name_en} - {self.doctor.name_en}"
            else:
                return self.patient.name_en
        except Exception:
            return "Deleted accounts!"

    def get_absolute_url(self):
        return reverse("base:request_details", kwargs={"id": self.id})

    def is_secure(self):
        return self.request.is_secure() if hasattr(self, "request") else False


class ConsultationHistory(models.Model):
    patient = models.ForeignKey(
        User, related_name="history_patient", on_delete=models.SET_NULL, null=True, blank=True
    )

    doctor = models.ForeignKey(
        User, related_name="history_doctor", on_delete=models.SET_NULL, null=True, blank=True
    )

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            if self.doctor:
                return f"{self.patient.name_en} - {self.doctor.name_en}"
            else:
                return self.patient.name_en
        except Exception:
            return "Deleted accounts!"

    class Meta:
        ordering = ("-created",)
        verbose_name_plural = "Consultations History"


class Document(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE)
    document = models.FileField(
        upload_to="Consultations/Documents",
        blank=True,
        null=True,
        validators=[validate_file_size],
        storage=RawMediaCloudinaryStorage(),
    )

    class Meta:
        ordering = ("consultation__created",)
