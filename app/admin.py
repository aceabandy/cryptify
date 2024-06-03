from django.contrib import admin
from .models import Signup
# Register your models here.
# admin.py
from django.contrib import admin
from .models import Profile, CryptoCurrency, CryptoBalance,Notification,Transaction,CryptoTransaction
from django.contrib import messages
class CryptoBalanceInline(admin.TabularInline):
    model = CryptoBalance
    extra = 1  # Number of extra forms to display

class ProfileAdmin(admin.ModelAdmin):
    inlines = [CryptoBalanceInline]

admin.site.register(Profile, ProfileAdmin)
admin.site.register(CryptoCurrency)

admin.site.register(Signup)
admin.site.register(Notification)
admin.site.register(Transaction)
@admin.action(description='Cancel selected transactions and notify users')
def cancel_transactions(modeladmin, request, queryset):
    for transaction in queryset:
        if transaction.status != 'cancelled':
            transaction.cancel_transaction()
            messages.success(request, f'Transaction {transaction.id} has been cancelled and user notified.')

class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount_naira', 'crypto_amount', 'cryptocurrency', 'status', 'created_at')
    actions = [cancel_transactions]

admin.site.register(CryptoTransaction, CryptoTransactionAdmin)