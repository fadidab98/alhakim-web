import math

from django.template import Library
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

register = Library()

@register.filter('humanized_timesince')
def humanized_timesince_filter(created_date):
    now = timezone.now()
        
    diff= now - created_date

    if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
        seconds= diff.seconds
        
        if seconds == 1:
            return str(seconds) +  _(" second")
        
        else:
            return str(seconds) + _(" seconds")

        

    if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
        minutes= math.floor(diff.seconds/60)

        if minutes == 1:
            return str(minutes) + _(" minute")
        
        else:
            return str(minutes) + _(" minutes")



    if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
        hours= math.floor(diff.seconds/3600)

        if hours == 1:
            return str(hours) + _(" hour")

        else:
            return str(hours) + _(" hours")

    # 1 day to 30 days
    if diff.days >= 1 and diff.days < 30:
        days= diff.days
    
        if days == 1:
            return str(days) + _(" day")

        else:
            return str(days) + _(" days")

    if diff.days >= 30 and diff.days < 365:
        months= math.floor(diff.days/30)
        

        if months == 1:
            return str(months) + _(" month")

        else:
            return str(months) + _(" months")


    if diff.days >= 365:
        years= math.floor(diff.days/365)

        if years == 1:
            return str(years) + _(" year")

        else:
            return str(years) + _(" years")