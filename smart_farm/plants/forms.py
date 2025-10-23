from django import forms
from .models import Plant

class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = [
            'field', 'plant_type', 'variety', 'planting_date', 
            'expected_harvest_date', 'area_hectares', 'growth_stage', 'notes'
        ]
        widgets = {
            'field': forms.Select(attrs={'class': 'form-control'}),
            'plant_type': forms.Select(attrs={'class': 'form-control'}),
            'variety': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bitki növü'}),
            'planting_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expected_harvest_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'area_hectares': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'growth_stage': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'field': 'Sahə',
            'plant_type': 'Bitki Növü',
            'variety': 'Bitki Sortu',
            'planting_date': 'Əkin Tarixi',
            'expected_harvest_date': 'Gözlənilən Yığım Tarixi',
            'area_hectares': 'Sahə (hektar)',
            'growth_stage': 'Böyümə Mərhələsi',
            'notes': 'Qeydlər',
        }

class PlantSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label ='Axtarış',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bitki sortuna görə axtar...'
        })
    )


class PlantFilterForm(forms.Form):
    plant_type = forms.ChoiceField(
        choices=[('','Bütün bitki növləri')] + Plant.PLANT_TYPES,  #birinci boslug '' ne ise yarayir? ne is gorur ve s.
        required=False,
        label='Bitki növü',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    growth_stage = forms.ChoiceField(
        choices=[('','Bütün böyümə mərhələləri')] + Plant.GROWTH_STAGES,
        required=False,
        label='Böyümə mərhələsi',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    status = forms.CharField(
        choice=[('','Bütün statuslar')] + Plant.STATUS_CHOICES,
        required=False,
        label='Status',
        widget=forms.Select(attrs={'class': 'form-control'}) 
    )