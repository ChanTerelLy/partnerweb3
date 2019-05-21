from django import forms
from .models import Auth

class AuthForm(forms.ModelForm):
    class Meta:
        model = Auth
        fields = ('sell_code', 'operator','password')