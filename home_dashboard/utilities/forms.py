"""
Generate the forms for the utilities app.
"""
from django import forms

from .models import Meter, Reading

class NewMeterForm(forms.ModelForm):
    """
    Form to create a new meter.
    """
    class Meta:
        model = Meter
        fields = '__all__'
        # Add CSS-class to the form
        widgets = {'meter_name': forms.TextInput({'class': 'form-control'}),
                   'unit_name': forms.TextInput({'class': 'form-control'})}


class ReadingForm(forms.ModelForm):
    """
    Form to new and edit a reading.
    """
    class Meta:
        model = Reading
        fields = '__all__'
        widgets = {
            'date': forms.DateInput({'class': 'datepicker', 'type': 'date'})
        }
