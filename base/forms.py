# forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=None, *args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contraseña'

class PositionForm(forms.Form):
    reorder = forms.CharField()
