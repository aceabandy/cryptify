from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal,InvalidOperation
from django.conf import settings
import requests
from django.core.mail import send_mail
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class CryptoCurrency(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class CryptoBalance(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='balances')
    cryptocurrency = models.ForeignKey(CryptoCurrency, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=17, decimal_places=8, default=Decimal('0.0'))

    def __str__(self):
        return f"{self.profile.user.username} - {self.cryptocurrency.name}"

    @property
    def current_price(self):
        url = f'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        headers = {
            'X-CMC_PRO_API_KEY': settings.COINMARKETCAP_API_KEY,
            'Accepts': 'application/json'
        }
        params = {
            'symbol': self.cryptocurrency.symbol,
            'convert': 'USD'
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        try:
            price = Decimal(data['data'][self.cryptocurrency.symbol.upper()]['quote']['USD']['price'])
        except (KeyError, InvalidOperation):
            price = Decimal('0.0')
        return price

    @property
    def value(self):
        return self.balance * self.current_price


class Signup(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name   


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.created_at}"
    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount} - {self.date}" 



class CryptoTransaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_naira = models.DecimalField(max_digits=10, decimal_places=2)
    crypto_amount = models.DecimalField(max_digits=10, decimal_places=8)
    cryptocurrency = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_image = models.ImageField(upload_to='transactions/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def cancel_transaction(self):
        self.status = 'cancelled'
        self.save()
        send_mail(
            'P2P Trade Cancelled',
            'Your P2P trade has been cancelled by the admin.',
            'from@example.com',
            [self.user.email],
            fail_silently=False,
        )
