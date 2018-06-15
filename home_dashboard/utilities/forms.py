"""
Generate the forms for the utilities app.
"""
from django import forms

class NewMeterForm(forms.Form):
    """
    Form to create a new meter.
    """
    meter_name = forms.CharField(max_length=30)
    unit_name = forms.CharField(max_length=10)

    #Add CSS-class to the form
    meter_name.widget.attrs['class'] = 'form-control'
    unit_name.widget.attrs['class'] = 'form-control'