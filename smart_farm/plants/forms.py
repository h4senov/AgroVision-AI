from django import forms
from .models import Plant
from django.db.models import Sum
class PlantForm(forms.ModelForm):
    class Meta:
        model = Plant
        fields = [
            'field', 'plant_type', 'variety', 'planting_date', 
            'expected_harvest_date', 'area_hectares', 'growth_stage', 'notes', 'image'
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
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'   
            }),
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
            'image': 'Şəkil',
        }

    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get('field')
        requested_area = cleaned_data.get('area_hectares')

        if field and requested_area:
            # Sənin Field modelində sahənin adı 'area_hectares'dir
            total_field_capacity = field.area_hectares
            
            # Bu sahədə artıq əkilmiş olan digər aktiv bitkilərin cəmi sahəsi
            existing_plants_query = Plant.objects.filter(field=field, status='active')
            
            # Əgər redaktə ediriksə (edit), öz sahəmizi cəmdən çıxırıq
            if self.instance.pk:
                existing_plants_query = existing_plants_query.exclude(pk=self.instance.pk)
            
            already_used_area = existing_plants_query.aggregate(Sum('area_hectares'))['area_hectares__sum'] or 0
            available_area = total_field_capacity - already_used_area

            # Yoxlama məntiqi
            if requested_area > available_area:
                raise forms.ValidationError({
                    'area_hectares': f"Bu sahədə kifayət qədər yer yoxdur! "
                                     f"Ümumi sahə: {total_field_capacity} ha, "
                                     f"İstifadə olunub: {already_used_area} ha, "
                                     f"Boş yer: {available_area} ha."
                })
        
        return cleaned_data
    

class PlantSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Axtarış',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Bitki sortuna görə axtar...'
        })
    )


class PlantFilterForm(forms.Form):
    plant_type = forms.ChoiceField(
        choices=[('', 'Bütün bitki növləri')] + Plant.PLANT_TYPES,
        required=False,
        label='Bitki növü',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    growth_stage = forms.ChoiceField(
        choices=[('', 'Bütün böyümə mərhələləri')] + Plant.GROWTH_STAGES,
        required=False,
        label='Böyümə mərhələsi',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'Bütün statuslar')] + Plant.STATUS_CHOICES,
        required=False,
        label='Status',
        widget=forms.Select(attrs={'class': 'form-control'})
    )