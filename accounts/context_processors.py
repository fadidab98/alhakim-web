from base.models import Consultation
from django.db.models import Q


def doctor_messages(request):
    if request.user.is_authenticated and request.user.is_doctor:
        inbox_count = Consultation.objects.filter(doctor=request.user, read=False).count()
        unknown_inbox_count = Consultation.objects.filter(Q(doctor=None) | Q(specialty=None), read=False).count()
    else:
        inbox_count = None
        unknown_inbox_count = None

    return {
        'inbox_count': inbox_count,
        'unknown_inbox_count': unknown_inbox_count
    }
