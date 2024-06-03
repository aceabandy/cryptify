from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# Define your custom login form
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        "placeholder": "Enter username",
    }))
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "input",
        "type": "password",
        "placeholder": "Enter password",
    }))
class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        "class": "input",
        "type": "text",
        "placeholder": "Enter username",
    }), label="Username")
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "input",
        "type": "email",
        "placeholder": "Enter your email",
    }), label="Email")

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "input",
        "placeholder": "Enter your password",
        "id": "password1",  # Add an id for easier selection in JavaScript
    }), label="Password")

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        "class": "input",
        "placeholder": "Repeat password",
        "id": "password2",  # Add an id for easier selection in JavaScript
    }), label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']    





class DepositForm(forms.Form):
    username = forms.CharField(max_length=100)
    cryptocurrency = forms.ChoiceField(choices=[
        ('btc', 'BTC'),
        ('eth', 'ETH'),
        ('ltc', 'LTC'),
        ('doge', 'DOGE'),
        ('sol', 'SOL'),
        ('bnb', 'BNB'),
        ('ton', 'TONCOIN'),
        ('bch', 'BCH'),
        ('tron', 'TRON'),
        

    ])         