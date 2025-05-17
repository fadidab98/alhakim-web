from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from specialties.models import Specialty

from .models import Doctor, Patient, User


class CreateUserForm(UserCreationForm):
    phone_error = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'phone_error'}), required=False)
    full_phone = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'full_phone'}), label=_('رقم الهاتف'), required=False)

    class Meta:
        model = User
        fields = ('name_en', 'email', 'phone_error', 'full_phone')

        labels = {
            'name_en': _('الاسم الكامل بالإنجليزية'),
            'email': _('الإيميل'),
            'full_phone': _('رقم الهاتف'),
        }

        icons = {
            'name_en': 'fa-id-card',
            'email': 'fa-envelope',
            'password1': 'fa-unlock-keyhole',
            'password2': 'fa-unlock-keyhole',
            'full_phone': 'fa-phone',
        }

    def clean(self):
        cleaned_data = super().clean()

        phone_error = cleaned_data['phone_error']

        if phone_error != '' and phone_error != 'empty':
            self.add_error('full_phone', _('رقم الهاتف الذي أدخلته خاطئ!'))

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        
        try:
            doctor = kwargs.pop('doctor')
        except:
            doctor = None

        super().__init__(*args, **kwargs)

        if doctor == None:
            self.fields.pop('email')

        icons = getattr(self.Meta, 'icons', dict())

        for field_name, field in self.fields.items():
            if field_name in icons:
                field.icon = icons[field_name]

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()

        return instance
    

class UpdateUserForm(UserChangeForm):
    password = None

    phone_error = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'phone_error'}), required=False)
    full_phone = forms.CharField(widget=forms.HiddenInput(attrs={'id': 'full_phone'}), label=_('رقم الهاتف'), required=False)

    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'new_password'}), label=_('كلمة المرور الجديدة'), required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'id': 'confirm_new_password'}), label=_('تأكيد كلمة المرور الجديدة'), required=False)

    class Meta:
        model = User
        fields = ('name_en', 'new_password','confirm_new_password', 'phone_error', 'full_phone')

        labels = {
            'name_en': _('الاسم الكامل بالإنجليزية'),
            'full_phone': _('رقم الهاتف'),
        }

        icons = {
            'name_en': 'fa-id-card',
            'new_password': 'fa-unlock-keyhole',
            'confirm_new_password': 'fa-unlock-keyhole',
            'full_phone': 'fa-phone',
        }

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['phone_error'] != '' and cleaned_data['phone_error'] != 'empty':
            self.add_error('full_phone', _('رقم الهاتف الذي أدخلته خاطئ!'))
        
        if cleaned_data['new_password'] != cleaned_data['confirm_new_password']:
            self.add_error('new_password', _('كلمات المرور التي أدخلتها غير متطابقة!'))

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icons = getattr(self.Meta, 'icons', dict())

        for field_name, field in self.fields.items():
            if field_name in icons:
                field.icon = icons[field_name]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

        return instance


class CreateDoctorForm(forms.ModelForm):
    old_specialty = forms.ModelChoiceField(queryset=Specialty.objects.all(), empty_label=_('-- اختر الاختصاص --'), label=_('اختيار اختصاص موجود سابقاً'), widget=forms.Select(), required=False)
    
    new_specialty_ar = forms.CharField(max_length=100, widget=forms.TextInput(), label=_('اسم الاختصاص الجديد بالعربية'), required = False)
    new_specialty_en = forms.CharField(max_length=100, widget=forms.TextInput(), label=_('اسم الاختصاص الجديد بالإنجليزية'), required = False)

    class Meta:
        model = Doctor
        exclude = ('user', 'specialty')

        labels = {
            'profile_pic': _('الصورة الشخصية'),
            'bio_ar': _('لمحة عن الطبيب بالعربية'),
            'bio_en': _('لمحة عن الطبيب بالإنجليزية'),
            'syndicate_card': _('صورة البطاقة النقابية'),
            'syndicate_number': _('الرقم النقابي'),
            'cv': _('السيرة الذاتية'),
            'certificate': _('أعلى درجة علمية'),
            'work_location_ar': _('عنوان العمل بالعربية'),
            'work_location_en': _('عنوان العمل بالإنجليزية'),
            'name_ar': _('الاسم الكامل بالعربية'),
            'city_ar': _('المدينة بالعربية'),
            'email': _('الإيميل'),
            'country': _('الدولة'),
            'city_en': _('المدينة بالإنجليزية'),
        }

        icons = {
            'new_specialty_ar': 'fa-briefcase-medical',
            'new_specialty_en': 'fa-briefcase-medical',
            'old_specialty': 'fa-briefcase-medical',
            'bio_ar': 'fa-address-card',
            'bio_en': 'fa-address-card',
            'profile_pic': 'fa-image',
            'certificate': 'fa-certificate',
            'syndicate_card': 'fa-id-card-clip',
            'syndicate_number': 'fa-id-card-clip',
            'cv': 'fa-file',
            'work_location_ar': 'fa-location-dot',
            'work_location_en': 'fa-location-dot',
            'name_ar': 'fa-id-card',
            'city_ar': 'fa-location',
            'country': 'fa-globe',
            'city_en': 'fa-location',
            'email': 'fa-envelope',
        }

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['old_specialty'] is None and cleaned_data['new_specialty_en'] == '':
            self.add_error('new_specialty_ar', _('يجب اختيار اختصاص الطبيب!'))
        if cleaned_data['old_specialty'] is not None and cleaned_data['new_specialty_en'] != '':
            self.add_error('new_specialty_ar', _('يجب اختيار اختصاص واحد للطبيب!'))

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        icons = getattr(self.Meta, 'icons', dict())

        for field_name, field in self.fields.items():
            if field_name in icons:
                field.icon = icons[field_name]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data['new_specialty_ar'] != '':
            instance.specialty = Specialty.objects.get_or_create(name_ar=self.cleaned_data['new_specialty_ar'], name_en=self.cleaned_data['new_specialty_en'])[0]  
        else:
            instance.specialty = self.cleaned_data.get('old_specialty')
        
        if commit:
            instance.save()

        return instance
    

class UpdateDoctorForm(forms.ModelForm):
    old_specialty = forms.ModelChoiceField(queryset=Specialty.objects.all(), empty_label=_('-- اختر الاختصاص --'), label=_('اختيار اختصاص موجود سابقاً'), widget=forms.Select(), required=False)
    
    new_specialty_ar = forms.CharField(max_length=100, widget=forms.TextInput(), label=_('اسم الاختصاص الجديد بالعربية'), required = False)
    new_specialty_en = forms.CharField(max_length=100, widget=forms.TextInput(), label=_('اسم الاختصاص الجديد بالإنجليزية'), required = False)

    class Meta:
        model = Doctor
        exclude = ('user', 'specialty')

        labels = {
            'profile_pic': _('الصورة الشخصية'),
            'bio_ar': _('لمحة عن الطبيب بالعربية'),
            'bio_en': _('لمحة عن الطبيب بالإنجليزية'),
            'syndicate_card': _('صورة البطاقة النقابية'),
            'syndicate_number': _('الرقم النقابي'),
            'cv': _('السيرة الذاتية'),
            'certificate': _('أعلى درجة علمية'),
            'work_location_ar': _('عنوان العمل بالعربية'),
            'work_location_en': _('عنوان العمل بالإنجليزية'),
            'name_ar': _('الاسم الكامل بالعربية'),
            'city_ar': _('المدينة بالعربية'),
            'email': _('الإيميل'),
            'country': _('الدولة'),
            'city_en': _('المدينة بالإنجليزية'),
        }

        icons = {
            'new_specialty_ar': 'fa-briefcase-medical',
            'new_specialty_en': 'fa-briefcase-medical',
            'old_specialty': 'fa-briefcase-medical',
            'bio_ar': 'fa-address-card',
            'bio_en': 'fa-address-card',
            'profile_pic': 'fa-image',
            'certificate': 'fa-certificate',
            'syndicate_card': 'fa-id-card-clip',
            'syndicate_number': 'fa-id-card-clip',
            'cv': 'fa-file',
            'work_location_ar': 'fa-location-dot',
            'work_location_en': 'fa-location-dot',
            'name_ar': 'fa-id-card',
            'city_ar': 'fa-location',
            'country': 'fa-globe',
            'city_en': 'fa-location',
            'email': 'fa-envelope',
        }

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data['old_specialty'] is None and cleaned_data['new_specialty_en'] == '':
            self.add_error('new_specialty_ar', _('يجب اختيار اختصاص الطبيب!'))
        if cleaned_data['old_specialty'] is not None and cleaned_data['new_specialty_en'] != '':
            self.add_error('new_specialty_ar', _('يجب اختيار اختصاص واحد للطبيب!'))

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initial['old_specialty'] = self.instance.specialty

        icons = getattr(self.Meta, 'icons', dict())

        for field_name, field in self.fields.items():
            if field_name in icons:
                field.icon = icons[field_name]

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.cleaned_data['new_specialty_ar'] != '':
            instance.specialty = Specialty.objects.get_or_create(name_ar=self.cleaned_data['new_specialty_ar'], name_en=self.cleaned_data['new_specialty_en'])[0]  
        else:
            instance.specialty = self.cleaned_data.get('old_specialty')
        
        if commit:
            instance.save()

        return instance


class DoctorDeleteForm(forms.ModelForm):
    specialty = forms.ModelChoiceField(queryset=Specialty.objects.all(), empty_label=_('-- اختر اختصاص الطبيب --'), label=_('الاختصاص'), widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    doctor = forms.ModelChoiceField(queryset=User.objects.none(), label=_('الطبيب'), empty_label=_('-- قم باختيار الاختصاص أولاً --'),  widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    
    class Meta:
        model = Doctor
        fields = ('specialty', 'doctor')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'specialty' in self.data:
            if self.data['specialty'] != '-1':
                try:
                    specialty_id = int(self.data['specialty'])
                    specialty = Specialty.objects.get(id=specialty_id)
                    self.fields['doctor'].queryset = User.objects.filter(is_doctor=True, profile_doctor__specialty=specialty)
                except:
                    pass
            
            else:
                self.fields['doctor'].label = _('-- قم باختيار الاختصاص أولاً --')
                self.fields['doctor'].queryset = User.objects.none()


class CreatePatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ('user',)


class UpdatePatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ('user',)


class PasswordResetForm(forms.Form):
    phone = forms.CharField(max_length=50, label=_("رقم الهاتف"))
    email = forms.EmailField(label=_("الإيميل"))