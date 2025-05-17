from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Doctor, Patient, User

admin.site.unregister(Group)

class DoctorInline(admin.StackedInline):
    model = Doctor
    extra = 1

class PatientInline(admin.StackedInline):
    model = Patient
    extra = 1

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'phone', 'is_active', 'is_staff')
    list_editable = ('is_active', 'is_staff')
    list_filter = ('is_doctor', 'is_active', 'is_patient')
    list_per_page = 20
    search_fields = ('name_en', 'profile_doctor__name_ar', )
    ordering = ('-created', 'name_en',)
    readonly_fields = ('password',)

    inlines = (DoctorInline,)
    other_inlines = (PatientInline,)

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        inlines = self.inlines

        if obj and obj.is_doctor:
            inlines = self.inlines
        elif obj and obj.is_patient:
            inlines = self.other_inlines

        for inline_class in inlines:
            inline = inline_class(self.model, self.admin_site)
            if request:
                if not (inline.has_add_permission(request, obj) or
                        inline.has_change_permission(request, obj) or
                        inline.has_delete_permission(request, obj)):
                    continue
                if not inline.has_add_permission(request, obj):
                    inline.max_num = 0
            inline_instances.append(inline)

        return inline_instances
    
    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            yield inline.get_formset(request, obj)

admin.site.register(User, CustomUserAdmin)