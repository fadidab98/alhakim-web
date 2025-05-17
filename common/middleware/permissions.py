from django.core.exceptions import PermissionDenied


class SuperUserOnlyMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            if request.user.is_staff == False:
                raise PermissionDenied
        except:
            raise PermissionDenied
        
        return super(SuperUserOnlyMixin, self).dispatch(request, *args, **kwargs)


class DoctorUserOnlyMixin(object):
    def dispatch(self, request, *args, **kwargs):
        try:
            if request.user.is_doctor == False:
                raise PermissionDenied
        except:
            raise PermissionDenied
        
        return super().dispatch(request, *args, **kwargs)