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

class FilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Start Date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'End Date'}))
    min_amount = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Amount'}))
    max_amount = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Amount'}))
    due_15_days = forms.BooleanField(required=False, label="Show Due > 15 Days (Sold > 15 days ago)", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
