from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_file_size(value):
        try:
            if value:
                limit = 10 * 1024 * 1024
                if value.size > limit:
                    raise ValidationError(_('File size must be less than 10 MB.'))
        except Exception as ex:
            print(ex)
            pass