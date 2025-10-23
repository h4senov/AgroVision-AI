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
        
class FieldSearchForm(forms.Form):
    
    search = forms.CharField(
        required=False,
        label='Axtarış',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sahə adına görə axtar...',
            'style': 'max-width: 300px;'
        })
    )

class FieldFilterForm(forms.Form):
     
    SOIL_CHOICES = [
        ('', 'Bütün torpaq növləri'),
        ('sandy', 'Qumlu'),
        ('clay', 'Gil'),
        ('loamy', 'Qara torpaq'),
        ('silty', 'Gilli'),
        ('peat', 'Torf'),
    ]
    
    soil_type = forms.ChoiceField(
        choices=SOIL_CHOICES,
        required=False,
        label='Torpaq növü',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'style': 'max-width: 250px;'
        })
    )

    min_area = forms.DecimalField(
        required=False,
        label='Min sahə (hektar)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01'
        })
    )
    
    max_area = forms.DecimalField(
        required=False, 
        label='Max sahə (hektar)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '100.00',
            'step': '0.01'
        })
    )