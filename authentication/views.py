from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from binance.client import Client
from binance.exceptions import BinanceAPIException
from .models import CustomUser
from django.db import IntegrityError
from django.db import transaction
import re
from django.contrib.auth.decorators import login_required
from .forms import SetPasswordForm
from tradebots.models import CryptoBots, MartBotState
from django.http import JsonResponse
from tradebots.bots import MartBot
from django.db import models
from .forms import StopBotForm

global crypto_bots
crypto_bots = {}

User = CustomUser

# Create your views here.
def home(request):
    return render(request, 'authentication/index.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        api_key = request.POST['api_key']
        api_secret = request.POST['api_secret']
        
        
        if pass1 == pass2:
            if len(pass1) < 8 or not re.search(r"\d", pass1) or not re.search(r"[A-Z]", pass1) or not re.search(r"[a-z]", pass1):
                messages.error(request, 'Your password must be at least 8 characters long and contain at least one number, one uppercase letter, and one lowercase letter.')
                return redirect('authentication:signup')

            try:
                with transaction.atomic():
                    user = CustomUser.objects.create_user(username, email, pass1)
                    user.first_name = fname
                    user.last_name = lname
                    user.is_active = False

                    # Create an instance of the Binance API client
                    client = Client(api_key, api_secret, tld='us')

                    # Make a test request to check the connection
                    account_info = client.get_account()

                    # If the request succeeds, store the API credentials on the user
                    user.api_key = api_key
                    user.api_secret = api_secret

                    activateEmail(request, user, email)

                    user.save()

                    messages.success(request, 'Your Account has been Successfully Created!')
                    return redirect('authentication:home')
            except BinanceAPIException:
                messages.error(request, 'Binance API is incorrect')
            except IntegrityError:
                messages.error(request, 'Email address is already in use. Please choose a different email.')
        else:
            messages.error(request, 'Your passwords do not match')

    all_messages = messages.get_messages(request)
    return render(request, 'authentication/signup.html', {'messages': all_messages})


def signin(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Sign in successful")
            return redirect('authentication:userhome')
            
        else:
            messages.error(request, 'Sign in Error')
            return redirect('authentication:signin')
    
    return render(request, 'authentication/signin.html')

def signout(request):
    logout(request)
    messages.success(request, 'Sign out Success')
    return redirect('authentication:home')

def activateEmail(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('authentication/activate_account.html', {
        'user': user.first_name,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user.first_name}, please go to your email {to_email} inbox and click on the received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')
        
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login to your account.')
        return redirect('authentication:home')
    else:
        messages.error(request, 'Activation link is invalid!')
    
    return redirect('authentication:home')




@login_required
def userhome(request):
    bot_names = CryptoBots.objects.values_list('bot_name', flat=True)

    bot_data = []

    for bot_name in bot_names:
        try:
            bot_state = MartBotState.objects.get(bot_name=bot_name)
            total_profit = bot_state.total_profit

            form = StopBotForm(initial={'bot_name': bot_name})
            bot_data.append({'bot': {'bot_name': bot_name, 'total_profit': total_profit}, 'form': form})
        except MartBotState.DoesNotExist:
            pass
            #messages.success(request, 'Go to Trading Bots and create your first bot to get started!')

    context = {
        'bot_data': bot_data,
    }

    if request.method == 'POST':
        form = StopBotForm(request.POST)
        if form.is_valid():
            bot_name = form.cleaned_data['bot_name']
            print("Received bot name:", bot_name)
            try:
                crypto_bot = CryptoBots.objects.get(bot_name=bot_name)
            except CryptoBots.DoesNotExist:
                messages.error(request, 'Bot instance not found.')
            else:
                print('deleting')
                bot_state = MartBotState.objects.get(bot_name=bot_name)
                bot_state.delete()

                crypto_bot.delete()
                messages.success(request, 'Bot stopped successfully.')
            return render(request, 'authentication/del_success.html')

    return render(request, 'authentication/userhome.html', context)

@login_required
def password_change(request):
    user = request.user
    form = SetPasswordForm(user)
    return render(request, 'password_reset_confirm.html', {'form': form})



