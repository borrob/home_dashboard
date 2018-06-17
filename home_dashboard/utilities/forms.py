"""
Generate the forms for the utilities app.
"""
from django import forms

from .models import Reading

class NewMeterForm(forms.Form):
    """
    Form to create a new meter.
    """
    meter_name = forms.CharField(max_length=30)
    unit_name = forms.CharField(max_length=10)

    #Add CSS-class to the form
    meter_name.widget.attrs['class'] = 'form-control' # pylint: disable=no-member
    unit_name.widget.attrs['class'] = 'form-control' # pylint: disable=no-member


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

