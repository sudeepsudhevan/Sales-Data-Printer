from django.contrib import admin
from .models import MoneyReceived, ItemSold

@admin.register(MoneyReceived)
class MoneyReceivedAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'amount')
    list_filter = ('date',)
    ordering = ('-date',)

@admin.register(ItemSold)
class ItemSoldAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'weight', 'price', 'total')
    list_filter = ('date',)
    ordering = ('-date',)
    readonly_fields = ('total',)
