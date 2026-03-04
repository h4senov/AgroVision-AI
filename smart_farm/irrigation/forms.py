from django import forms
from .models import IrrigationSchedule
from fields.models import Field
from plants.models import Plant
class IrrigationScheduleForm(forms.ModelForm):
    class Meta:
        model = IrrigationSchedule
        fields = [
            'field', 'plant', 'irrigation_date', 'irrigation_type', 
            'water_volume_liters', 'status', 'is_automated', 
            'start_time', 'end_time',   
            'applied_fertilizer', 'notes'
        ]
        
        # HTML5 Tarix və Saat seçicilərini aktivləşdirmək üçün widgets
        widgets = {
            'irrigation_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Əlavə qeydlər...'}),
            'field': forms.Select(attrs={'class': 'form-select'}),
            'plant': forms.Select(attrs={'class': 'form-select'}),
            'irrigation_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'water_volume_liters': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'soil_moisture_level': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'energy_consumption': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'applied_fertilizer': forms.TextInput(attrs={'class': 'form-control'}),
            'is_automated': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs): # 'user' arqumentini buradan çıxarırıq
        user = kwargs.pop('user', None) # User-i yalnız kwargs-dan götürürük
        super().__init__(*args, **kwargs)
        if user:
            self.fields['field'].queryset = Field.objects.filter(user=user)
            self.fields['plant'].queryset = Plant.objects.filter(field__user=user)

    def clean(self):
        """
        Xüsusi yoxlamalar: Bitmə vaxtı başlama vaxtından əvvəl ola bilməz.
        """
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        field = cleaned_data.get('field')
        plant = cleaned_data.get('plant')

        if field and plant and plant.field != field:
            plant_label = f"{plant.get_plant_type_display()} ({plant.variety})" if plant.variety else plant.get_plant_type_display()
            self.add_error('plant', f"Seçilmiş bitki ({plant_label}) bu sahəyə ({field.name}) aid deyil!")
        
        if start_time and end_time:
            if end_time < start_time:
                # Səhv mesajını 'end_time' sahəsinə yapışdırırıq
                self.add_error('end_time', "Bitmə vaxtı başlama vaxtından tez ola bilməz.")
        
        return cleaned_data