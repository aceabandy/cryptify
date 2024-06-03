from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views
from .views import password_reset_request, password_reset_confirm
from app.forms import UserLoginForm

urlpatterns = [
    path('', views.index, name='index'),
    path('cryptify/', views.cryptify, name='cryptify'),
    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html", authentication_form=UserLoginForm), name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdrawal/', views.withdraw, name='withdraw'),
    path('receive/', views.receive, name='receive'),

    # Password reset views
    path('accounts/password_reset/', password_reset_request, name='password_reset'),
    path('accounts/password_reset/done/', TemplateView.as_view(template_name='password-reset/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('accounts/reset/done/', TemplateView.as_view(template_name='password-reset/password_reset_complete.html'), name='password_reset_complete'),


    #buy_crypto_account
    path('buy-crypto/', views.buy_crypto, name='buy_crypto'),
    path('preview-conversion/', views.preview_conversion, name='preview_conversion'),
    path('p2p/', views.p2p_page, name='p2p_page'),
    path('cancel-trade/', views.cancel_trade, name='cancel_trade'),
    
]

