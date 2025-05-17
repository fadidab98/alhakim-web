from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Consultation

User = get_user_model()


@receiver(post_save, sender=Consultation)
def send_email_to_user(sender, instance, created, **kwargs):
    if created:
        subject = "New Incoming Consultation Request"

        if instance.doctor is None:

            message = "Dear Dr. {}, \n\n There is a new consultation request with an unknown doctor / specialty. Please log in to your account to view and respond to it.".format(
                "Fouad"
            )

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ["berrofouad66@gmail.com"])
        else:
            doctor = User.objects.get(phone__icontains=instance.doctor)

            message_en = "Hello! \n \n Dear {}, \n \n You have a new medical consultation submitted through Al-Hakim platform for medical consultations. Please review the consultation and take the necessary steps. \n \n Thank you for your attention and prompt response.\n \n Best regards, \n Administration of Al-Hakim Free Medical Consultations Platform."

            message_ar = "مرحبًا! \n \n عزيزي/عزيزتي {}, \n \n لديك استشارة طبية جديدة تم تقديمها من خلال منصة الحكيم للاستشارات الطبية. يرجى مراجعة الاستشارة واتخاذ الخطوات اللازمة. \n \n شكرًا لاهتمامك واستجابتك السريعة. \n \n مع خالص التحية، \n إدارة منصة الحكيم للاستشارات الطبية المجانية."

            doctor_name_en = doctor.name_en

            try:
                doctor_name_ar = doctor.name_ar
            except Exception:
                doctor_name_ar = doctor.name_en

            message_en = message_en.format(doctor_name_en)
            message_ar = message_ar.format(doctor_name_ar)

            message = message_en + " \n \n \n \n " + message_ar

            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [doctor.email])
