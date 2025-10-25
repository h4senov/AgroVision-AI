from django import forms
from .models import Inventory

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = [
            'item_name', 'item_code', 'category', 'quantity', 'unit',
            'min_stock_level', 'max_stock_level', 'supplier_name',
            'unit_price', 'expiration_date', 'storage_location', 'notes'
        ]
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Məhsul adını daxil edin...'}),
            'item_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MHS-001'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'kq, litr, ədəd...'}),
            'min_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-control'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'storage_location': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InventorySearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Axtarış',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Məhsul adına görə axtar...'
        })
    )

class InventoryFilterForm(forms.Form):
    category = forms.ChoiceField(
        choices=[('', 'Bütün kateqoriyalar')] + Inventory.CATEGORY_CHOICES,
        required=False,
        label='Kateqoriya',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    stock_status = forms.ChoiceField(
        choices=[('', 'Bütün stoklar'), ('low', 'Aşağı stok'), ('normal', 'Normal'), ('high', 'Yüksək stok')],
        required=False,
        label='Stok statusu',
        widget=forms.Select(attrs={'class': 'form-control'})
    )