from django.urls import path
from .views import RegistrationView, UsernameValidationView, EmailValidationView, ValidationView, LoginView, LogoutView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register/', RegistrationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name="validate_username"),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name="validate_email"),
    path('activate/<uidb64>/<token>', ValidationView.as_view(), name="activate"),
    path('logout', LogoutView.as_view(), name='logout')
]