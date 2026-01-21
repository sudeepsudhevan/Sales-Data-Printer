from django import forms
from .models import MoneyReceived, ItemSold

class MoneyReceivedForm(forms.ModelForm):
    class Meta:
        model = MoneyReceived
        fields = ['date', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }

class ItemSoldForm(forms.ModelForm):
    class Meta:
        model = ItemSold
        fields = ['date', 'weight', 'price']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
