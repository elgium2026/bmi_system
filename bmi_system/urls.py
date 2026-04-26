from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts.views import login_view, logout_view, register, bmi_view, export_excel

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', login_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', register, name='register'),
    path('bmi/', bmi_view, name='bmi'),

    path('export/', export_excel, name='export_excel'),

    # PASSWORD RESET
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]