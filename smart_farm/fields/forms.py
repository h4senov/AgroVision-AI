from django import forms
from .models import Field

class FieldForm(forms.ModelForm):
    
    class Meta:
        model = Field
        fields = ['name','area_hectares','soil_type']
        widgets = {
            
            'name':forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' Field name '}),
            'area_hectares': forms.NumberInput(attrs={'class': 'form-control','step':'0.01' }),
            'soil_type': forms.Select(attrs={'class':'form-control'}),
            
        }
        labels = {
            'name':'Field Name',
            'area_hectares': 'Area (hectares)',
            'soil_type': 'Soil Type',
        }
        