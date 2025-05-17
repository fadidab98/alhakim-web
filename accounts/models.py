import uuid

from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import IntegrityError, models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from common.validators.validate_file_size import validate_file_size
from specialties.models import Specialty


class UserManager(BaseUserManager):
    def create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("The Phone number must be set!")

        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)

        try:
            user.save()
        except IntegrityError:
            raise ValueError(_("هذا الرقم مأخوذ سابقا, الرجاء استخدام رقم اخر"))

        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        try:
            self.create_user(phone, password, **extra_fields)
        except IntegrityError:
            raise ValueError(_("هذا الرقم مأخوذ سابقا, الرجاء استخدام رقم اخر"))


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)

    name_en = models.CharField(max_length=70)

    email = models.EmailField(unique=True, blank=True, null=True)

    phone = models.CharField(max_length=100, unique=True)

    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["name_en"]

    objects = UserManager()

    def __str__(self):
        try:
            return self.phone
        except Exception:
            return "Deleted Account!"

    class Meta:
        ordering = ("name_en",)


class Doctor(models.Model):
    class CERTIFICATE(models.TextChoices):
        BACHELOR = "BACHELOR", _("Bachelor's Degree")
        MASTER = "MASTER", _("Master's Degree")
        DOCTORAL = "DOCTORAL", _("Doctoral's Degree")

    user = models.OneToOneField(
        User, related_name="profile_doctor", on_delete=models.CASCADE, null=True, blank=True
    )

    name_ar = models.CharField(max_length=70, null=True, blank=True)

    city_ar = models.CharField(max_length=100, null=True, blank=True)

    profile_pic = models.ImageField(
        upload_to="Doctors/Profile-Pictures", validators=[validate_file_size]
    )

    syndicate_card = models.FileField(
        upload_to="Doctors/Syndicate-Cards",
        validators=[validate_file_size],
        storage=RawMediaCloudinaryStorage(),
    )
    syndicate_number = models.CharField(max_length=100, blank=True)

    country = models.CharField(max_length=100, null=True)
    city_en = models.CharField(max_length=100, null=True)

    bio_ar = models.TextField(blank=True)
    bio_en = models.TextField(blank=True)

    certificate = models.CharField(
        max_length=20, choices=CERTIFICATE.choices, default=CERTIFICATE.BACHELOR
    )
    cv = models.FileField(
        upload_to="Doctors/CVs",
        validators=[validate_file_size],
        storage=RawMediaCloudinaryStorage(),
    )

    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, blank=True, null=True)

    work_location_ar = models.TextField(null=True, blank=True)
    work_location_en = models.TextField(null=True, blank=True)

    def __str__(self):
        try:
            return self.user.name_en
        except Exception:
            return "Deleted Account!"

    def get_absolute_url(self):
        return reverse("accounts:profile", kwargs={"id": self.user.id})

    class Meta:
        ordering = ("user__name_en",)


class Patient(models.Model):
    user = models.OneToOneField(User, related_name="profile_patient", on_delete=models.CASCADE)

    def __str__(self):
        try:
            return self.user.name_en
        except Exception as ex:
            return "Deleted Account!"

    class Meta:
        ordering = ("user__name_en",)
