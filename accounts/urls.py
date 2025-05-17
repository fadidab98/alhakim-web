from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/doctor/', views.RegisterDoctor.as_view(), name='register_doctor'),
    path('register/patient/', views.RegisterPatient.as_view(), name='register_patient'),
    
    path('update/doctor/<str:id>/', views.UpdateDoctor.as_view(), name='update_doctor'),
    path('update/patient/<str:id>/', views.UpdatePatient.as_view(), name='update_patient'),

    path('profile/<str:id>/', views.DoctorProfile.as_view(), name='profile'),

    path('delete/', views.DeleteDoctor.as_view(), name='delete_doctor'),

    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),

    path('accounts/reset-password/', views.PhonePasswordResetView.as_view(), name='reset_password'),
    path('accounts/reset-password-sent/', views.PhonePasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', views.PhonePasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
