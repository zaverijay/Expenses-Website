from django.shortcuts import redirect, render
from django.views import View
import json, os
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_generator
from django.contrib.sites.models import Site
from django.contrib import auth


# Create your views here.

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'Sorry email is already taken'}, status=409)
        return JsonResponse({'email_valid': True})
    



class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']

        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should contain only alphanumeric charaters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'Sorry Username is already taken'}, status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')
    
    def post(self, request):

        # messages.success(request, "Successful")
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        contex = {
            'fieldValues' : request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():

                if len(password)<6:
                    messages.error(request, 'Password is too short')
                    return render(request, 'authentication/register.html', contex)
                
                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = False
                user.save()

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                # domain = get_current_site(request).domain
                current_site = Site.objects.get_current()
                domain = current_site.domain
                link = reverse('activate', kwargs={'uidb64':uidb64, 'token':token_generator.make_token(user)})

                activate_url = 'https://'+domain+link

                email_subject = 'Activate your account'
                email_body = 'Hi ' + user.username + ' Please use this link to verify your account \n' + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    os.getenv('DEFAULT_FROM_EMIAL'),
                    [email],
                )
                email.send(fail_silently=False)
                messages.success(request, 'Account created successful')
                return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')
    

class ValidationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not token_generator.check_token(user, token):
                return redirect('login'+'?message=' + 'User already activated')
            
            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save() 

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as e:
            pass
            
        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome ' + ' you are now logged in')
                    return redirect('expenses')

                messages.error(request, 'Account is not active, please check your mail')
                return render(request, 'authentication/login.html')
            messages.error(request, 'Invalid credentials, try again')
            return render(request, 'authentication/login.html')
        
        messages.error(request, 'Please fill all the fields')
        return render(request, 'authentication/login.html')
    

class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    